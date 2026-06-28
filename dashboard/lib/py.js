import { spawn } from "child_process";
import { existsSync } from "fs";
import path from "path";

// dashboard/ lives inside the repo; the pipeline runs from the repo root.
const REPO_ROOT = path.resolve(process.cwd(), "..");

function pyBin() {
  const venv = path.join(REPO_ROOT, ".venv", "bin", "python");
  return existsSync(venv) ? venv : "python3";
}

// Run the Python bridge (m3_engine/api.py) and parse its single JSON line.
export function runBridge(args) {
  return new Promise((resolve, reject) => {
    const proc = spawn(pyBin(), [path.join("m3_engine", "api.py"), ...args], {
      cwd: REPO_ROOT,
      env: {
        ...process.env,
        PYTHONWARNINGS: "ignore",
        ANONYMIZED_TELEMETRY: "False",
        GRPC_VERBOSITY: "NONE",
        TOKENIZERS_PARALLELISM: "false",
      },
    });
    let out = "";
    let err = "";
    proc.stdout.on("data", (d) => (out += d));
    proc.stderr.on("data", (d) => (err += d));
    proc.on("error", reject);
    proc.on("close", (code) => {
      if (code !== 0) return reject(new Error(err.trim() || `bridge exited ${code}`));
      try {
        resolve(JSON.parse(out));
      } catch {
        reject(new Error("bridge returned non-JSON: " + out.slice(0, 300)));
      }
    });
  });
}

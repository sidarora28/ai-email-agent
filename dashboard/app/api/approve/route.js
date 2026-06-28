import { runBridge } from "../../../lib/py";

export const dynamic = "force-dynamic";
export const maxDuration = 120; // first run may open a browser for Gmail compose auth

export async function POST(req) {
  try {
    const { id, body } = await req.json();
    if (!id) return Response.json({ error: "no id" }, { status: 400 });
    const args = ["approve", "--id", id];
    if (typeof body === "string") args.push("--body", body);
    const data = await runBridge(args);
    return Response.json(data);
  } catch (e) {
    return Response.json({ error: String(e.message || e) }, { status: 500 });
  }
}

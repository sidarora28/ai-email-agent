import { runBridge } from "../../../lib/py";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const data = await runBridge(["inbox"]);
    return Response.json(data);
  } catch (e) {
    return Response.json({ error: String(e.message || e) }, { status: 500 });
  }
}

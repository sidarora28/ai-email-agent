import { runBridge } from "../../../lib/py";

export const dynamic = "force-dynamic";
export const maxDuration = 300; // drafting runs the claude CLI sequentially

export async function POST(req) {
  try {
    const { ids } = await req.json();
    if (!Array.isArray(ids) || ids.length === 0) {
      return Response.json({ error: "no ids selected" }, { status: 400 });
    }
    const data = await runBridge(["draft", "--ids", ids.join(",")]);
    return Response.json(data);
  } catch (e) {
    return Response.json({ error: String(e.message || e) }, { status: 500 });
  }
}

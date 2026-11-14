export async function GET() {
  const customer = {
    name: "Guest User",
    email: "guest@faceframe.com",
    plan: "demo",
  };

  return Response.json({ customer });
}

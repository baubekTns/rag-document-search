export async function testBackend() {
  const res = await fetch("http://localhost:8000/");
  return res.json();
}

// Mock backend for POST /api/cart/add (dev only). Replace with the real service when available.
const products = {
  "p-1": { id: "p-1", name: "Wireless Headphones", price: 59.99, stock: 5 },
  "p-2": { id: "p-2", name: "Coffee Mug", price: 9.5, stock: 0 },
  "p-3": { id: "p-3", name: "Notebook", price: 4.25, stock: 12 },
};

const carts = new Map(); // userId -> { productId: quantity }

export function cartApiMock() {
  return {
    name: "cart-api-mock",
    configureServer(server) {
      server.middlewares.use("/api/cart/add", (req, res) => {
        if (req.method !== "POST") {
          res.statusCode = 405;
          return res.end();
        }
        let body = "";
        req.on("data", (chunk) => (body += chunk));
        req.on("end", () => {
          res.setHeader("Content-Type", "application/json");
          let payload;
          try {
            payload = JSON.parse(body || "{}");
          } catch {
            res.statusCode = 400;
            return res.end(JSON.stringify({ error: "Invalid JSON" }));
          }
          const { userId, productId } = payload;
          const product = products[productId];
          if (!userId || !product) {
            res.statusCode = 400;
            return res.end(JSON.stringify({ error: "userId and a valid productId are required" }));
          }
          if (product.stock <= 0) {
            res.statusCode = 409;
            return res.end(JSON.stringify({ error: "Out of stock" }));
          }
          const cart = carts.get(userId) ?? {};
          cart[productId] = (cart[productId] ?? 0) + 1;
          carts.set(userId, cart);
          const count = Object.values(cart).reduce((sum, qty) => sum + qty, 0);
          res.statusCode = 200;
          res.end(JSON.stringify({ ok: true, count }));
        });
      });
    },
  };
}

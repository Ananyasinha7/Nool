// Contract fixtures: lets screens be built and demoed before the API answers (VITE_USE_FIXTURES=true).
import buyerOrder from "../../../contract/fixtures/buyerOrder.json";
import orders from "../../../contract/fixtures/orders.json";
import supCards from "../../../contract/fixtures/supCards.json";
import warnings from "../../../contract/fixtures/warnings.json";

export const fixtures: Record<string, unknown> = {
  "/orders": orders,
  "/sup/orders": supCards,
  "/warnings": warnings,
  "/buyer/orders": [buyerOrder],
};
export { buyerOrder as buyerOrderFixture };

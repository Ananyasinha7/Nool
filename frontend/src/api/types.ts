// Friendly names over the generated OpenAPI types. Never hand-copy API shapes: change the Pydantic model,
// regenerate (npm run gen:types), and fix the compiler errors.
import type { components } from "./types.gen";

type S = components["schemas"];
export type OrderHealth = S["OrderHealth"];
export type OrderSummary = S["OrderSummary"];
export type OrderDetail = S["OrderDetail"];
export type OrderCreate = S["OrderCreate"];
export type MilestoneOut = S["MilestoneOut"];
export type SupOrderCard = S["SupOrderCard"];
export type LogInput = S["LogInput"];
export type LogRow = S["LogRow"];
export type NoteView = S["NoteView"];
export type WarningView = S["WarningView"];
export type ExFactoryChangeOut = S["ExFactoryChangeOut"];
export type ExFactoryChangeIn = S["ExFactoryChangeIn"];
export type TnaTemplateOut = S["TnaTemplateOut"];
export type Lookups = S["Lookups"];
export type OutboxOut = S["OutboxOut"];
export type MeOut = S["MeOut"];
export type BuyerOrderView = S["BuyerOrderView"];
export type BuyerOrderDetail = S["BuyerOrderDetail"];

export type Health = OrderHealth["health"];
export type StageKey = NonNullable<OrderHealth["activeStage"]>;
export type NoteCategory = NoteView["category"];
export type EditableCategory = S["CategoryIn"]["category"];
export type ReasonCode = ExFactoryChangeIn["reasonCode"];

/** ApiError is the one error shape the backend returns (Doc3 section 5.3). */
export interface ApiErrorBody {
  code: "VALIDATION" | "UNAUTHENTICATED" | "FORBIDDEN" | "NOT_FOUND" | "CONFLICT" | "RATE_LIMITED" | "SERVER";
  message: string;
  fields?: Record<string, string> | null;
}

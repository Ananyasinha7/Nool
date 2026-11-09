/**
 * Safe UUIDv4 generator. Uses native crypto.randomUUID when available (secure contexts / localhost),
 * with an RFC4122 v4 fallback for non-secure HTTP contexts (e.g. mobile phone over local LAN IP).
 */
export function generateUUID(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}


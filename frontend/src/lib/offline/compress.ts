import config from "../../../../contract/config.json";

/** Max side 1280 px, JPEG 0.7, target <= 200 KB (Doc3 section 10). Pure part, tested. */
export function fitSize(w: number, h: number, max = 1280): { w: number; h: number } {
  const scale = Math.min(1, max / Math.max(w, h));
  return { w: Math.round(w * scale), h: Math.round(h * scale) };
}

export class PhotoTooLarge extends Error {}

export async function compressImage(file: Blob): Promise<Blob> {
  const bmp = await createImageBitmap(file);
  const { w, h } = fitSize(bmp.width, bmp.height);
  const canvas = document.createElement("canvas");
  canvas.width = w; canvas.height = h;
  canvas.getContext("2d")?.drawImage(bmp, 0, 0, w, h);
  bmp.close();
  for (const q of [0.7, 0.6, 0.5, 0.4]) {
    const blob = await new Promise<Blob | null>((res) => canvas.toBlob(res, "image/jpeg", q));
    if (blob && blob.size <= 200_000) return blob;
    if (blob && q === 0.4) {
      if (blob.size > config.photoMaxBytes) throw new PhotoTooLarge(); // reject above photoMaxBytes
      return blob;
    }
  }
  throw new PhotoTooLarge();
}

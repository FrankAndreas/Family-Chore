// Task photos are scaled down in the browser before upload: the server stores them at
// 1280 px anyway, and full-size phone photos (3 to 8 MB) come close to its 10 MB limit.
const MAX_SIDE = 1600;

// Returns a JPEG of at most MAX_SIDE px on the longer side; a photo the browser can't
// decode (or a non-image) goes up as it is, and the server decides.
export async function shrinkPhoto(file: File): Promise<Blob> {
    if (!file.type.startsWith('image/')) return file;
    try {
        const bitmap = await createImageBitmap(file);
        const scale = Math.min(1, MAX_SIDE / Math.max(bitmap.width, bitmap.height));
        const canvas = document.createElement('canvas');
        canvas.width = Math.round(bitmap.width * scale);
        canvas.height = Math.round(bitmap.height * scale);
        const context = canvas.getContext('2d');
        if (!context) return file;
        context.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
        bitmap.close();
        return await new Promise(resolve => canvas.toBlob(blob => resolve(blob ?? file), 'image/jpeg', 0.85));
    } catch {
        return file;
    }
}

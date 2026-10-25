import { afterEach, describe, expect, it, vi } from 'vitest';
import { shrinkPhoto } from './shrinkPhoto';

const photo = new File(['x'], 'IMG_0001.jpg', { type: 'image/jpeg' });

// jsdom has neither createImageBitmap nor a drawing canvas: stub both and record the canvas size
function stubBrowser(width: number, height: number) {
    const close = vi.fn();
    vi.stubGlobal('createImageBitmap', vi.fn().mockResolvedValue({ width, height, close }));
    const canvas = {
        width: 0,
        height: 0,
        getContext: () => ({ drawImage: vi.fn() }),
        toBlob: (done: (blob: Blob | null) => void, type: string) => done(new Blob(['small'], { type })),
    };
    const create = document.createElement.bind(document);
    vi.spyOn(document, 'createElement').mockImplementation((tag: string) =>
        (tag === 'canvas' ? canvas : create(tag)) as HTMLElement);
    return { canvas, close };
}

describe('shrinkPhoto', () => {
    afterEach(() => {
        vi.restoreAllMocks();
        vi.unstubAllGlobals();
    });

    it('scales a large photo to 1600 px on the longer side as JPEG', async () => {
        const { canvas, close } = stubBrowser(4032, 3024);
        const result = await shrinkPhoto(photo);
        expect(canvas.width).toBe(1600);
        expect(canvas.height).toBe(1200);
        expect(result.type).toBe('image/jpeg');
        expect(result).not.toBe(photo);
        expect(close).toHaveBeenCalled();
    });

    it('never enlarges a small photo', async () => {
        const { canvas } = stubBrowser(800, 600);
        await shrinkPhoto(photo);
        expect(canvas.width).toBe(800);
        expect(canvas.height).toBe(600);
    });

    it('returns the original when the browser cannot decode it', async () => {
        vi.stubGlobal('createImageBitmap', vi.fn().mockRejectedValue(new Error('HEIC')));
        expect(await shrinkPhoto(photo)).toBe(photo);
    });

    it('leaves a non-image untouched', async () => {
        const text = new File(['x'], 'notes.txt', { type: 'text/plain' });
        expect(await shrinkPhoto(text)).toBe(text);
    });
});

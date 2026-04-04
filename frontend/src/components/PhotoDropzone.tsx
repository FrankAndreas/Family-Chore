import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';

interface PhotoDropzoneProps {
    instanceId: number;
    photo: File | null;
    onPhotoChange: (instanceId: number, file: File | null) => void;
}

// Helper component to manage Object URL lifecycle
const PhotoPreview: React.FC<{ file: File }> = ({ file }) => {
    const [url, setUrl] = useState<string>('');

    useEffect(() => {
        const objectUrl = URL.createObjectURL(file);
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setUrl(objectUrl);
        return () => URL.revokeObjectURL(objectUrl);
    }, [file]);

    return (
        <img
            src={url}
            alt="Task completion verification photo"
            style={{ width: '100%', height: 'auto', borderRadius: '4px', objectFit: 'cover', border: '1px solid var(--border-color)' }}
        />
    );
};

const PhotoDropzone: React.FC<PhotoDropzoneProps> = ({ instanceId, photo, onPhotoChange }) => {
    const { t } = useTranslation();

    const handleDragOver = useCallback((e: React.DragEvent<HTMLLabelElement>) => {
        e.preventDefault();
        e.currentTarget.classList.add('drag-active');
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent<HTMLLabelElement>) => {
        e.preventDefault();
        e.currentTarget.classList.remove('drag-active');
    }, []);

    const handleDrop = useCallback((e: React.DragEvent<HTMLLabelElement>) => {
        e.preventDefault();
        e.currentTarget.classList.remove('drag-active');
        const file = e.dataTransfer.files ? e.dataTransfer.files[0] : null;
        if (file && file.type.startsWith('image/')) {
            onPhotoChange(instanceId, file);
        }
    }, [instanceId, onPhotoChange]);

    const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files ? e.target.files[0] : null;
        onPhotoChange(instanceId, file);
    }, [instanceId, onPhotoChange]);

    return (
        <div className="photo-upload-section mt-3">
            <label
                className="dropzone-container flex-col-center border-dashed border-2 rounded-md p-4 bg-secondary cursor-pointer max-w-sm w-full mx-auto"
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    accept="image/*"
                    capture="environment"
                    className="hidden-file-input"
                    onChange={handleFileChange}
                />
                {photo ? (
                    <div className="photo-upload-box">
                        <PhotoPreview file={photo} />
                        <div className="photo-replace-btn">
                            ✓
                        </div>
                        <div className="photo-replace-text">
                            {t('dashboard.photoReplace', 'Tap to replace photo')}
                        </div>
                    </div>
                ) : (
                    <>
                        <div className="photo-upload-icon">📸</div>
                        <div className="photo-upload-text">
                            {t('dashboard.photoTake', 'Tap to take photo or drop image here')}
                        </div>
                        <small className="photo-upload-hint">
                            {t('dashboard.photoRequired', 'Verification required')}
                        </small>
                    </>
                )}
            </label>
        </div>
    );
};

export default PhotoDropzone;

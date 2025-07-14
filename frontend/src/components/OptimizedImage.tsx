import React, { useState, useRef, useEffect } from 'react';

interface OptimizedImageProps {
  src: string;
  alt: string;
  className?: string;
  width?: number;
  height?: number;
  sizes?: string;
  priority?: boolean;
  placeholder?: 'blur' | 'empty';
  blurDataURL?: string;
  onLoad?: () => void;
  onError?: () => void;
}

const OptimizedImage: React.FC<OptimizedImageProps> = ({
  src,
  alt,
  className = '',
  width,
  height,
  sizes = '100vw',
  priority = false,
  placeholder = 'empty',
  blurDataURL,
  onLoad,
  onError,
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [isInView, setIsInView] = useState(priority);
  const imgRef = useRef<HTMLImageElement>(null);

  // Intersection Observer for lazy loading
  useEffect(() => {
    if (priority || isInView) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      {
        rootMargin: '50px',
        threshold: 0.1,
      }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, [priority, isInView]);

  // Generate responsive image sources
  const generateSrcSet = (originalSrc: string) => {
    const srcWithoutExt = originalSrc.replace(/\.[^/.]+$/, '');
    const ext = originalSrc.match(/\.[^/.]+$/)?.[0] || '.jpg';
    
    // For external URLs or if no width specified, return original
    if (originalSrc.startsWith('http') || !width) {
      return originalSrc;
    }

    // Generate different sizes
    const sizes = [width * 0.5, width, width * 1.5, width * 2].map(Math.round);
    return sizes
      .map(size => `${srcWithoutExt}_${size}w${ext} ${size}w`)
      .join(', ');
  };

  // WebP support detection and source generation
  const generateWebPSrc = (originalSrc: string) => {
    if (originalSrc.startsWith('http')) return originalSrc;
    return originalSrc.replace(/\.(jpg|jpeg|png)$/i, '.webp');
  };

  const handleLoad = () => {
    setIsLoaded(true);
    onLoad?.();
  };

  const handleError = () => {
    setHasError(true);
    onError?.();
  };

  // Placeholder component
  const renderPlaceholder = () => {
    if (placeholder === 'blur' && blurDataURL) {
      return (
        <img
          src={blurDataURL}
          alt=""
          className={`${className} filter blur-sm transition-opacity duration-300 ${
            isLoaded ? 'opacity-0' : 'opacity-100'
          }`}
          style={{ width, height }}
        />
      );
    }

    return (
      <div
        className={`${className} bg-gray-200 animate-pulse flex items-center justify-center transition-opacity duration-300 ${
          isLoaded ? 'opacity-0' : 'opacity-100'
        }`}
        style={{ width, height }}
      >
        <svg
          className="w-8 h-8 text-gray-400"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fillRule="evenodd"
            d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"
            clipRule="evenodd"
          />
        </svg>
      </div>
    );
  };

  // Error fallback
  if (hasError) {
    return (
      <div
        className={`${className} bg-gray-100 flex items-center justify-center border border-gray-200`}
        style={{ width, height }}
      >
        <svg
          className="w-8 h-8 text-gray-400"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fillRule="evenodd"
            d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
            clipRule="evenodd"
          />
        </svg>
      </div>
    );
  }

  return (
    <div className="relative overflow-hidden" style={{ width, height }}>
      {!isLoaded && placeholder !== 'empty' && renderPlaceholder()}
      
      {(isInView || priority) && (
        <picture>
          {/* WebP source for modern browsers */}
          <source
            srcSet={generateSrcSet(generateWebPSrc(src))}
            sizes={sizes}
            type="image/webp"
          />
          
          {/* Fallback for browsers that don't support WebP */}
          <img
            ref={imgRef}
            src={src}
            srcSet={generateSrcSet(src)}
            sizes={sizes}
            alt={alt}
            className={`${className} transition-opacity duration-300 ${
              isLoaded ? 'opacity-100' : 'opacity-0'
            }`}
            style={{ width, height }}
            loading={priority ? 'eager' : 'lazy'}
            decoding="async"
            onLoad={handleLoad}
            onError={handleError}
          />
        </picture>
      )}
    </div>
  );
};

export default OptimizedImage; 
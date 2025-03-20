import React, { useState, useRef, useEffect } from 'react';

const slideData = [
  {
    index: 0,
    headline: 'New Fashion Apparel',
    button: 'Shop now',
    src: 'https://s3-us-west-2.amazonaws.com/s.cdpn.io/225363/fashion.jpg'
  },
  {
    index: 1,
    headline: 'In The Wilderness',
    button: 'Book travel',
    src: 'https://s3-us-west-2.amazonaws.com/s.cdpn.io/225363/forest.jpg'
  },
  {
    index: 2,
    headline: 'For Your Current Mood',
    button: 'Listen',
    src: 'https://s3-us-west-2.amazonaws.com/s.cdpn.io/225363/guitar.jpg'
  },
  {
    index: 3,
    headline: 'Focus On The Writing',
    button: 'Get Focused',
    src: 'https://s3-us-west-2.amazonaws.com/s.cdpn.io/225363/typewriter.jpg'
  }
];

const Slide = ({ slide, current, handleSlideClick }) => {
  const { src, button, headline, index } = slide;
  const slideRef = useRef(null);
  
  const handleMouseMove = (event) => {
    const el = slideRef.current;
    const r = el.getBoundingClientRect();
    
    el.style.setProperty('--x', `${event.clientX - (r.left + Math.floor(r.width / 2))}`);
    el.style.setProperty('--y', `${event.clientY - (r.top + Math.floor(r.height / 2))}`);
  };
  
  const handleMouseLeave = () => {
    slideRef.current.style.setProperty('--x', '0');
    slideRef.current.style.setProperty('--y', '0');
  };
  
  const imageLoaded = (event) => {
    event.target.style.opacity = 1;
  };
  
  let slideClasses = 'relative flex flex-col items-center justify-center h-full w-full mx-4 text-center text-white opacity-25 transition-all duration-300 ease-in-out';
  
  if (current === index) {
    slideClasses = 'relative flex flex-col items-center justify-center h-full w-full mx-4 text-center text-white opacity-100 transition-all duration-300 ease-in-out cursor-default';
  } else if (current - 1 === index) {
    slideClasses = 'relative flex flex-col items-center justify-center h-full w-full mx-4 text-center text-white opacity-25 transition-all duration-300 ease-in-out cursor-w-resize hover:opacity-50 hover:translate-x-2';
  } else if (current + 1 === index) {
    slideClasses = 'relative flex flex-col items-center justify-center h-full w-full mx-4 text-center text-white opacity-25 transition-all duration-300 ease-in-out cursor-e-resize hover:opacity-50 hover:-translate-x-2';
  }
  
  return (
    <li 
      ref={slideRef}
      className={slideClasses}
      onClick={() => handleSlideClick(index)}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden rounded-sm bg-[#1D1F2F] transition-transform duration-150 ease-in-out">
        <img 
          className="absolute top-[-5%] left-[-5%] w-[110%] h-[110%] object-cover opacity-0 pointer-events-none select-none transition-all duration-600 ease-in-out"
          alt={headline}
          src={src}
          onLoad={imageLoaded}
        />
      </div>
      
      <div className="invisible opacity-0 p-4 relative transition-transform duration-600 ease-in-out current-slide-content">
        <h2 className="text-8vmin font-semibold font-serif">{headline}</h2>
        <button className="mt-8 px-10 py-4 bg-[#6B7A8F] text-white border-none rounded cursor-pointer hover:focus:outline-[#6D64F7] hover:focus:outline-offset-2 hover:focus:outline-3 active:translate-y-px">{button}</button>
      </div>
    </li>
  );
};

const SliderControl = ({ type, title, handleClick }) => {
  return (
    <button 
      className={`flex items-center justify-center w-12 h-12 bg-transparent border-3 border-transparent rounded-full focus:border-[#6D64F7] focus:outline-none ${type === 'previous' ? 'rotate-180' : ''}`}
      title={title} 
      onClick={handleClick}
    >
      <svg className="w-full fill-[#6B7A8F]" viewBox="0 0 24 24">
        <path d="M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z" />
      </svg>
    </button>
  );
};

const Slider = ({ heading, slides }) => {
  const [current, setCurrent] = useState(0);
  
  const handlePreviousClick = () => {
    const previous = current - 1;
    setCurrent(previous < 0 ? slides.length - 1 : previous);
  };
  
  const handleNextClick = () => {
    const next = current + 1;
    setCurrent(next === slides.length ? 0 : next);
  };
  
  const handleSlideClick = (index) => {
    if (current !== index) {
      setCurrent(index);
    }
  };
  
  const headingId = `slider-heading__${heading.replace(/\s+/g, '-').toLowerCase()}`;
  
  useEffect(() => {
    // Add global styles
    const style = document.createElement('style');
    style.innerHTML = `
      @import url('https://fonts.googleapis.com/css?family=Playfair+Display:700|IBM+Plex+Sans:500&display=swap');
      
      :root {
        --base-duration: 600ms;
        --base-ease: cubic-bezier(0.25, 0.46, 0.45, 0.84);
      }
      
      .current-slide-content {
        --d: 60;
      }
      
      li.opacity-100 .current-slide-content {
        animation: fade-in calc(var(--base-duration) / 2) var(--base-ease) forwards;
        visibility: visible;
      }
      
      @keyframes fade-in {
        from { opacity: 0 }
        to { opacity: 1 }
      }
    `;
    document.head.appendChild(style);
    
    return () => {
      document.head.removeChild(style);
    };
  }, []);
  
  return (
    <div className="relative w-[70vmin] h-[70vmin] mx-auto" aria-labelledby={headingId}>
      <ul 
        className="flex absolute transition-transform duration-600 ease-out"
        style={{
          transform: `translateX(-${current * (100 / slides.length)}%)`,
          margin: '0 -4vmin'
        }}
      >
        <h3 id={headingId} className="sr-only">{heading}</h3>
        
        {slides.map(slide => (
          <Slide
            key={slide.index}
            slide={slide}
            current={current}
            handleSlideClick={handleSlideClick}
          />
        ))}
      </ul>
      
      <div className="absolute flex justify-center w-full top-full mt-4">
        <SliderControl 
          type="previous"
          title="Go to previous slide"
          handleClick={handlePreviousClick}
        />
        
        <SliderControl 
          type="next"
          title="Go to next slide"
          handleClick={handleNextClick}
        />
      </div>
    </div>
  );
};

const Carousal = () => {
  return (
    <div className="flex items-center justify-center h-screen w-screen overflow-x-hidden bg-[#101118] font-sans">
      <Slider heading="Example Slider" slides={slideData} />
    </div>
  );
};

export default Carousal;
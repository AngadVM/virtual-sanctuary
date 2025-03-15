import React from 'react';

const BentoGrid = ({ data }) => {
  // Create columns based on data
  // We need 4 columns for desktop, 2 for mobile
  const columns = 4;
  const columnsData = Array.from({ length: columns }, () => []);
  
  // Ensure data is an array
  const imageData = Array.isArray(data) ? data : Object.values(data);
  
  // Distribute images across columns
  imageData.forEach((image, index) => {
    const columnIndex = index % columns;
    columnsData[columnIndex].push(image);
  });

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {columnsData.map((column, columnIndex) => (
        <div key={columnIndex} className="grid gap-4">
          {column.map((image, imageIndex) => (
            <div key={`${columnIndex}-${imageIndex}`}>
              <img 
                className="h-auto max-w-full rounded-lg" 
                src={image.imgUrl || image.imageUrl} 
                alt={image.title || `Image ${columnIndex * column.length + imageIndex}`} 
              />
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

export default BentoGrid;
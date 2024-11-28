import React from 'react';

const ColorHints = ({ colors }) => {

    const colorArray = Object.keys(colors).map((colorKey) => colors[colorKey]);
    return <div className='flex flex-col no-download'>
        <div className='text-sm mt-1'>Farblegende</div>
        {colors && colorArray.map((color, i) => (
            <div key={i} className='p-1 text-xs m-1 text-white w-60 mx-auto' style={{background :color.female}}>{color.title}</div>
        ))}
    </div>
    
}

export default ColorHints;
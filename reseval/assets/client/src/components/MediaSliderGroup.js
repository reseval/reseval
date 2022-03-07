import React from 'react';
import Slider from 'rc-slider';

import Media from './Media';

import 'rc-slider/assets/index.css';

import '../css/components.css';


/******************************************************************************
 Radio buttons with corresponding media (audio, image, etc.)
 ******************************************************************************/


function MediaSlider({
                         file,
                         condition,
                         permutation,
                         index,
                         scores,
                         setScores,
                         setResponse,
                         reference,
                         active,
                         endeds,
                         setEndeds,
                         toucheds,
                         setToucheds
                     }) {
    /* Create a media element with a corresponding slider */
    function onChange(value) {
        /* Update scores */
        setScores(scores.map((score, i) => i === index ? value : score));
        // Pad with leading zeros
        const padded = scores.map(score => String(score).padStart(3, '0'));

        // Undo permutation
        const reverse_permutation = Array.from(
            Array(permutation.length).keys())
            .sort((a, b) => {
                return (
                    permutation[a] < permutation[b] ? -1 :
                        (permutation[b] < permutation[a]) | 0
                );
            });

        // Response is concatenation of zero-padded scores
        setResponse(
            reverse_permutation.map((index) => padded[index]).join(''));
        // Set slider touchedness to be true
        setToucheds(toucheds.map((touched, i) => i === index ? true : touched));

    }

    function onEnded() {
        /* Update what media has ended */
        setEndeds(endeds.map((ended, i) => i === index ? true : ended));
    }

    // Render slider and media
    return (
        <div className='mediaSliderBox' style={{'grid-column': index + 1}}>
            <div className='slider'>
                <Slider
                    value={scores[index]}
                    defaultValue={50}
                    startPoint={50}
                    marks={{0: 0, 25: 25, 50: 50, 75: 75, 100: 100}}
                    vertical={true}
                    disabled={!endeds[index]}
                    onChange={onChange}
                    railStyle={{backgroundColor: 'black'}}
                    trackStyle={{backgroundColor: 'black'}}
                    dotStyle={{
                        backgroundColor: 'black',
                        borderColor: 'black'
                    }}
                    activeDotStyle={{
                        backgroundColor: 'black',
                        borderColor: 'black'
                    }}
                    handleStyle={{
                        width: 20,
                        height: 20,
                        marginLeft: -8,
                        backgroundColor: 'black',
                        borderColor: 'white'
                    }}
                />
            </div>
            <div className='break'/>
            <Media
                src={condition + '/' + file}
                reference={reference}
                onEnded={onEnded}/>
        </div>
    );
};

export default function MediaSliderGroup({
                                             file,
                                             conditions,
                                             permutation,
                                             scores,
                                             setScores,
                                             setResponse,
                                             refs,
                                             active,
                                             endeds,
                                             setEndeds,
                                             toucheds,
                                             setToucheds
                                         }) {
    /* Create a group of media elements with corresponding sliders */
    const sliderGroup = conditions.map((condition, key) =>
        <MediaSlider
            file={file}
            condition={condition}
            permutation={permutation}
            index={key}
            key={key}
            scores={scores}
            setScores={setScores}
            setResponse={setResponse}
            reference={refs[key]}
            active={active}
            endeds={endeds}
            setEndeds={setEndeds}
            toucheds={toucheds}
            setToucheds={setToucheds}
        />
    );
    return <div className='mediaSliderGrid'>{sliderGroup}</div>;
};

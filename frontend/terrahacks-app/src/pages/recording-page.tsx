// In your main component or page
import React from 'react';
import AudioRecorder from '@/audio/audioRecorder'; // Adjust the import path as necessary

export default function RecordingPage() {
    const handleTranscriptionComplete = (transcription: any) => {
        console.log('Transcription completed:', transcription);
        // Do something with the transcribed text
        // For example, set it in a form field, save to state, etc.
    };

    return (
        <div>
            <h1>Speech to Text Demo</h1>
            <AudioRecorder onTranscriptionComplete={handleTranscriptionComplete} />
        </div>
    )
};

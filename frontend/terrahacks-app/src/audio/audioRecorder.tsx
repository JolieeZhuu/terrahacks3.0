import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Play, Square, Upload } from 'lucide-react';
import Button from '@/components/ui/button'

const AudioRecorder = ({ onTranscriptionComplete }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [transcription, setTranscription] = useState('');
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [error, setError] = useState('');

  const mediaRecorderRef = useRef(null);
  const audioRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);

  // Check browser support
  useEffect(() => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setError('MediaRecorder API is not supported in this browser');
    }
    if (!window.MediaRecorder) {
      setError('MediaRecorder is not supported in this browser');
    }
  }, []);

  // Timer for recording duration
  useEffect(() => {
    if (isRecording) {
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } else {
      clearInterval(timerRef.current);
    }

    return () => clearInterval(timerRef.current);
  }, [isRecording]);

  const startRecording = async () => {
    try {
      setError('');
      setRecordingTime(0);
      chunksRef.current = [];

      // Get user media
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000 // Good for speech recognition
        } 
      });
      
      streamRef.current = stream;

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus' // Good compression and quality
      });

      mediaRecorderRef.current = mediaRecorder;

      // Handle data available
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      // Handle recording stop
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setAudioBlob(blob);
        
        // Create URL for playback
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);

        // Stop all tracks
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
        }
      };

      // Start recording
      mediaRecorder.start(1000); // Collect data every second
      setIsRecording(true);

    } catch (err) {
      setError(`Error accessing microphone: ${err.message}`);
      console.error('Error starting recording:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const playRecording = () => {
    if (audioRef.current && audioUrl) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        audioRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  const transcribeAudio = async () => {
    if (!audioBlob) return;

    setIsTranscribing(true);
    setError('');

    try {
      // Option 1: Use Web Speech API (client-side)
      await transcribeWithWebSpeechAPI();
      
      // Option 2: Send to backend (uncomment to use)
      // await transcribeWithBackend();
      
    } catch (err) {
      setError(`Transcription failed: ${err.message}`);
    } finally {
      setIsTranscribing(false);
    }
  };

  // Client-side transcription using Web Speech API
  const transcribeWithWebSpeechAPI = () => {
    return new Promise((resolve, reject) => {
      if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        reject(new Error('Web Speech API not supported'));
        return;
      }

      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();

      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      let finalTranscript = '';

      recognition.onresult = (event) => {
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
          } else {
            interimTranscript += transcript;
          }
        }

        setTranscription(finalTranscript + interimTranscript);
      };

      recognition.onerror = (event) => {
        reject(new Error(`Speech recognition error: ${event.error}`));
      };

      recognition.onend = () => {
        setTranscription(finalTranscript.trim());
        if (onTranscriptionComplete) {
          onTranscriptionComplete(finalTranscript.trim());
        }
        resolve();
      };

      // Play the audio and start recognition
      if (audioRef.current) {
        audioRef.current.currentTime = 0;
        audioRef.current.play();
        recognition.start();
        
        audioRef.current.onended = () => {
          recognition.stop();
        };
      }
    });
  };

  // Backend transcription (alternative method)
  const transcribeWithBackend = async () => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');

    const response = await fetch('/api/transcribe', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error('Backend transcription failed');
    }

    const result = await response.json();
    setTranscription(result.transcription);
    
    if (onTranscriptionComplete) {
      onTranscriptionComplete(result.transcription);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const clearRecording = () => {
    setAudioBlob(null);
    setAudioUrl(null);
    setTranscription('');
    setRecordingTime(0);
    setError('');
  };

  return (
    <div className="p-6 max-w-md mx-auto bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-4 text-center">Audio Recorder</h2>
      
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* Recording Controls */}
      <div className="flex justify-center mb-4">
        {!isRecording ? (
          <Button
            onClick={startRecording}
            disabled={isTranscribing}
            className="flex items-center gap-2 bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg disabled:opacity-50"
          >
            <Mic size={20} />
            Start Recording
          </Button>
        ) : (
          <Button
            onClick={stopRecording}
            className="flex items-center gap-2 bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg"
          >
            <Square size={20} />
            Stop Recording
          </Button>
        )}
      </div>

      {/* Recording Timer */}
      {isRecording && (
        <div className="text-center mb-4">
          <div className="text-lg font-mono text-red-600">
            🔴 {formatTime(recordingTime)}
          </div>
        </div>
      )}

      {/* Playback Controls */}
      {audioUrl && (
        <div className="mb-4">
          <audio
            ref={audioRef}
            src={audioUrl}
            onEnded={() => setIsPlaying(false)}
            className="w-full mb-2"
            controls
          />
          
          <div className="flex gap-2 justify-center">
            <Button
              onClick={playRecording}
              className="flex items-center gap-2 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
            >
              {isPlaying ? <MicOff size={16} /> : <Play size={16} />}
              {isPlaying ? 'Pause' : 'Play'}
            </Button>
            
            <Button
              onClick={transcribeAudio}
              disabled={isTranscribing}
              className="flex items-center gap-2 bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded disabled:opacity-50"
            >
              <Upload size={16} />
              {isTranscribing ? 'Transcribing...' : 'Transcribe'}
            </Button>
            
            <Button
              onClick={clearRecording}
              className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded"
            >
              Clear
            </Button>
          </div>
        </div>
      )}

      {/* Transcription Result */}
      {transcription && (
        <div className="mt-4">
          <h3 className="font-semibold mb-2">Transcription:</h3>
          <div className="p-3 bg-gray-100 rounded border">
            {transcription}
          </div>
        </div>
      )}
    </div>
  );
};

export default AudioRecorder;
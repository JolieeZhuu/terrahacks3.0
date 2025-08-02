import React, { useState } from 'react';
import { emailAPI } from '../services/api';
import Input from '@/components/ui/input'
import Textarea from '@/components/ui/textarea'

const ComposeEmail = () => {
  const [email, setEmail] = useState({
    to: '',
    subject: '',
    body: '',
    html_body: ''
  });
  const [sending, setSending] = useState(false);

  const handleSend = async (e) => {
    e.preventDefault();
    setSending(true);
    
    try {
      const response = await emailAPI.sendEmail(email);
      alert('Email sent successfully!');
      setEmail({ to: '', subject: '', body: '', html_body: '' });
    } catch (error) {
      alert('Failed to send email');
    } finally {
      setSending(false);
    }
  };

  return (
    <form onSubmit={handleSend} className="max-w-lg mx-auto p-4">
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">To:</label>
        <Input
          type="email"
          value={email.to}
          onChange={(e) => setEmail({...email, to: e.target.value})}
          className="w-full p-2 border rounded"
          required
        />
      </div>
      
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">Subject:</label>
        <Input
          type="text"
          value={email.subject}
          onChange={(e) => setEmail({...email, subject: e.target.value})}
          className="w-full p-2 border rounded"
          required
        />
      </div>
      
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">Body:</label>
        <Textarea
          value={email.body}
          onChange={(e) => setEmail({...email, body: e.target.value})}
          className="w-full p-2 border rounded h-32"
          required
        />
      </div>
      
      <button 
        type="submit" 
        disabled={sending}
        className="bg-blue-500 text-white px-4 py-2 rounded disabled:bg-gray-400"
      >
        {sending ? 'Sending...' : 'Send Email'}
      </button>
    </form>
  );
};

export default ComposeEmail;
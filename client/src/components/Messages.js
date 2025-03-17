import React, { useState, useEffect } from 'react';

function Messages({ messages, setMessages }) {
  useEffect(() => {
    if (messages.length > 0) {
      const timer = setTimeout(() => setMessages([]), 5000); // Clear after 5s
      return () => clearTimeout(timer);
    }
  }, [messages]);

  return (
    <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50">
      {messages.map((msg, index) => (
        <div
          key={index}
          className={`p-4 mb-4 text-${msg.category === 'error' ? 'red' : 'green'}-500 bg-${msg.category === 'error' ? 'red' : 'green'}-100 rounded`}
        >
          {msg.message}
        </div>
      ))}
    </div>
  );
}

export default Messages;
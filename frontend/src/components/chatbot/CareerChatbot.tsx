import React, { useState, useRef, useEffect } from 'react';
import { FaComments, FaTimes, FaPaperPlane, FaRobot, FaUser } from 'react-icons/fa';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

interface CareerChatbotProps {
  isOpen: boolean;
  onToggle: () => void;
}

const CareerChatbot: React.FC<CareerChatbotProps> = ({ isOpen, onToggle }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hello! I'm your AI Career Advisor. I can help you with career advice, job application strategies, resume tips, and more. How can I assist you today?",
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    if (messagesEndRef.current && typeof messagesEndRef.current.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const careerAdviceResponses = {
    'resume': [
      "Here are some key resume tips:\n\n• Keep it concise (1-2 pages)\n• Use action verbs and quantifiable achievements\n• Tailor it to each job application\n• Include relevant keywords from job descriptions\n• Proofread carefully for errors\n• Use a clean, professional format",
      "Would you like me to help you with specific sections of your resume?"
    ],
    'interview': [
      "Interview preparation tips:\n\n• Research the company thoroughly\n• Practice common questions\n• Prepare STAR method responses\n• Dress appropriately\n• Arrive early\n• Bring extra copies of your resume\n• Prepare thoughtful questions to ask",
      "What type of interview are you preparing for?"
    ],
    'job search': [
      "Effective job search strategies:\n\n• Use multiple job boards and platforms\n• Network actively (LinkedIn, events)\n• Optimize your online presence\n• Apply to jobs that match 70%+ of requirements\n• Follow up after applications\n• Consider remote and hybrid opportunities",
      "What industry or role are you targeting?"
    ],
    'salary negotiation': [
      "Salary negotiation tips:\n\n• Research market rates for your role and location\n• Know your worth and minimum acceptable salary\n• Practice your pitch\n• Consider total compensation (benefits, equity)\n• Be confident but professional\n• Have a backup plan",
      "Are you negotiating a new offer or asking for a raise?"
    ],
    'career change': [
      "Career change guidance:\n\n• Assess your transferable skills\n• Research target industries and roles\n• Consider additional education or certifications\n• Network in your target field\n• Start with side projects or freelance work\n• Be patient with the transition",
      "What field are you looking to transition into?"
    ]
  };

  const generateBotResponse = (userMessage: string): string => {
    const lowerMessage = userMessage.toLowerCase();
    
    // Check for specific topics
    if (lowerMessage.includes('resume') || lowerMessage.includes('cv')) {
      return careerAdviceResponses.resume[0];
    }
    if (lowerMessage.includes('interview') || lowerMessage.includes('meeting')) {
      return careerAdviceResponses.interview[0];
    }
    if (lowerMessage.includes('job search') || lowerMessage.includes('find job') || lowerMessage.includes('apply')) {
      return careerAdviceResponses['job search'][0];
    }
    if (lowerMessage.includes('salary') || lowerMessage.includes('negotiate') || lowerMessage.includes('pay')) {
      return careerAdviceResponses['salary negotiation'][0];
    }
    if (lowerMessage.includes('career change') || lowerMessage.includes('switch') || lowerMessage.includes('transition')) {
      return careerAdviceResponses['career change'][0];
    }
    if (lowerMessage.includes('remote') || lowerMessage.includes('work from home')) {
      return "Remote work tips:\n\n• Set up a dedicated workspace\n• Maintain regular hours\n• Use communication tools effectively\n• Take breaks and stay active\n• Separate work and personal life\n• Build relationships with colleagues virtually";
    }
    if (lowerMessage.includes('skill') || lowerMessage.includes('learn')) {
      return "Skill development suggestions:\n\n• Identify in-demand skills in your field\n• Use online learning platforms (Coursera, Udemy, LinkedIn Learning)\n• Practice through projects and side work\n• Get certifications where relevant\n• Join professional communities\n• Stay updated with industry trends";
    }
    if (lowerMessage.includes('network') || lowerMessage.includes('connection')) {
      return "Networking strategies:\n\n• Attend industry events and conferences\n• Join professional associations\n• Use LinkedIn effectively\n• Participate in online communities\n• Offer value to others\n• Follow up and maintain relationships\n• Be genuine and authentic";
    }

    // Default responses
    const defaultResponses = [
      "I'd be happy to help you with career advice! Could you be more specific about what you'd like to know? For example, I can help with resume writing, interview preparation, job search strategies, salary negotiation, or career transitions.",
      "That's an interesting question! I can provide guidance on various career topics. What specific area would you like to focus on - resume optimization, interview skills, networking, or something else?",
      "I'm here to support your career development! To give you the best advice, could you tell me more about your current situation and what you're looking to achieve?",
      "Great question! I can help with career planning, job applications, professional development, and more. What's your primary career goal right now?"
    ];

    return defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue.trim(),
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate AI response delay
    setTimeout(() => {
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: generateBotResponse(userMessage.text),
        sender: 'bot',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botResponse]);
      setIsTyping(false);
    }, 1000 + Math.random() * 2000); // 1-3 second delay
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <>
      {/* Chatbot Toggle Button */}
      <button
        onClick={onToggle}
        className={`fixed bottom-6 right-6 z-50 w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg transition-all duration-300 flex items-center justify-center ${
          isOpen ? 'scale-0 opacity-0' : 'scale-100 opacity-100'
        }`}
        aria-label="Open Career Chatbot"
      >
        <FaComments className="w-6 h-6" />
      </button>

      {/* Chatbot Window */}
      <div
        className={`fixed bottom-6 right-6 z-50 w-96 h-[500px] bg-white rounded-lg shadow-2xl border border-gray-200 transition-all duration-300 ${
          isOpen ? 'scale-100 opacity-100' : 'scale-0 opacity-0 pointer-events-none'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-t-lg">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
              <FaRobot className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-semibold">Career Advisor AI</h3>
              <p className="text-xs text-blue-100">Online • Ready to help</p>
            </div>
          </div>
          <button
            onClick={onToggle}
            className="text-white/80 hover:text-white transition-colors"
            aria-label="Close Chatbot"
          >
            <FaTimes className="w-5 h-5" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 p-4 overflow-y-auto h-[380px]">
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    message.sender === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  <div className="flex items-start gap-2">
                    {message.sender === 'bot' && (
                      <FaRobot className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                    )}
                    <div className="flex-1">
                      <p className="text-sm whitespace-pre-line">{message.text}</p>
                      <p className={`text-xs mt-1 ${
                        message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}>
                        {formatTime(message.timestamp)}
                      </p>
                    </div>
                    {message.sender === 'user' && (
                      <FaUser className="w-4 h-4 text-blue-200 mt-0.5 flex-shrink-0" />
                    )}
                  </div>
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-800 rounded-lg p-3">
                  <div className="flex items-center gap-2">
                    <FaRobot className="w-4 h-4 text-blue-600" />
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center gap-2">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about careers, resumes, interviews..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              disabled={isTyping}
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isTyping}
              className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <FaPaperPlane className="w-4 h-4" />
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            AI-powered career advice • Free and confidential
          </p>
        </div>
      </div>
    </>
  );
};

export default CareerChatbot; 
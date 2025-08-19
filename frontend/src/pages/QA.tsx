import React, { useState, useEffect, useRef } from 'react';
import { FaSearch, FaQuestionCircle, FaLightbulb, FaBook, FaGraduationCap } from 'react-icons/fa';
import Layout from '../components/Layout';

interface QAItem {
  id: string;
  question: string;
  answer: string;
  category: string;
  tags: string[];
}

const QA: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [filteredQA, setFilteredQA] = useState<QAItem[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const searchRef = useRef<HTMLDivElement>(null);

  const qaData: QAItem[] = [
    // Job Search
    {
      id: '1',
      question: 'How do I find remote jobs?',
      answer: 'Use job boards like Remote.co, WeWorkRemotely, and FlexJobs. Network on LinkedIn, join remote work communities, and directly contact companies that offer remote positions.',
      category: 'Job Search',
      tags: ['remote', 'job search', 'networking']
    },
    {
      id: '2',
      question: 'What should I include in my resume?',
      answer: 'Include contact information, professional summary, work experience with quantifiable achievements, education, skills, and relevant certifications. Keep it concise and tailored to each job.',
      category: 'Resume',
      tags: ['resume', 'cv', 'application']
    },
    {
      id: '3',
      question: 'How do I prepare for a job interview?',
      answer: 'Research the company, practice common questions, prepare STAR method responses, dress appropriately, arrive early, and bring extra copies of your resume.',
      category: 'Interview',
      tags: ['interview', 'preparation', 'questions']
    },
    {
      id: '4',
      question: 'What is the STAR method?',
      answer: 'STAR stands for Situation, Task, Action, Result. It\'s a framework for answering behavioral interview questions by describing a specific situation, your role, actions taken, and outcomes achieved.',
      category: 'Interview',
      tags: ['star method', 'behavioral', 'interview']
    },
    {
      id: '5',
      question: 'How do I negotiate salary?',
      answer: 'Research market rates, know your worth, practice your pitch, consider total compensation, be confident but professional, and have a backup plan.',
      category: 'Salary',
      tags: ['salary', 'negotiation', 'compensation']
    },
    {
      id: '6',
      question: 'What are the best job search websites?',
      answer: 'LinkedIn, Indeed, Glassdoor, ZipRecruiter, Monster, and industry-specific job boards. Also check company career pages directly.',
      category: 'Job Search',
      tags: ['job boards', 'websites', 'search']
    },
    {
      id: '7',
      question: 'How do I write a cover letter?',
      answer: 'Address the hiring manager, explain why you\'re interested in the role, highlight relevant experience, show enthusiasm for the company, and end with a call to action.',
      category: 'Application',
      tags: ['cover letter', 'application', 'writing']
    },
    {
      id: '8',
      question: 'What should I wear to an interview?',
      answer: 'Dress professionally and appropriately for the company culture. Business formal for corporate roles, business casual for startups, and research the company\'s dress code.',
      category: 'Interview',
      tags: ['dress code', 'appearance', 'professional']
    },
    {
      id: '9',
      question: 'How do I answer "Tell me about yourself"?',
      answer: 'Provide a brief professional summary focusing on relevant experience, skills, and career goals. Keep it under 2 minutes and connect to the role you\'re applying for.',
      category: 'Interview',
      tags: ['self-introduction', 'opening', 'personal']
    },
    {
      id: '10',
      question: 'What questions should I ask in an interview?',
      answer: 'Ask about the role\'s responsibilities, team structure, company culture, growth opportunities, challenges, and next steps in the hiring process.',
      category: 'Interview',
      tags: ['questions', 'engagement', 'research']
    },
    // Career Development
    {
      id: '11',
      question: 'How do I switch careers?',
      answer: 'Assess transferable skills, research target industries, gain relevant experience through side projects or freelance work, network in your target field, and consider additional education.',
      category: 'Career Change',
      tags: ['career change', 'transition', 'skills']
    },
    {
      id: '12',
      question: 'What skills are in demand?',
      answer: 'Technical skills like programming, data analysis, AI/ML, cybersecurity, and soft skills like communication, leadership, problem-solving, and adaptability.',
      category: 'Skills',
      tags: ['skills', 'demand', 'trends']
    },
    {
      id: '13',
      question: 'How do I build a professional network?',
      answer: 'Attend industry events, join professional associations, use LinkedIn effectively, participate in online communities, offer value to others, and maintain relationships.',
      category: 'Networking',
      tags: ['networking', 'connections', 'relationships']
    },
    {
      id: '14',
      question: 'Should I get a certification?',
      answer: 'Certifications can boost your resume and demonstrate expertise. Research which ones are valued in your industry and align with your career goals.',
      category: 'Education',
      tags: ['certification', 'credentials', 'learning']
    },
    {
      id: '15',
      question: 'How do I ask for a raise?',
      answer: 'Document your achievements, research market rates, schedule a meeting with your manager, present your case professionally, and be prepared to negotiate.',
      category: 'Salary',
      tags: ['raise', 'promotion', 'compensation']
    },
    // Remote Work
    {
      id: '16',
      question: 'How do I stay productive working remotely?',
      answer: 'Set up a dedicated workspace, maintain regular hours, use productivity tools, take breaks, separate work and personal life, and communicate effectively with your team.',
      category: 'Remote Work',
      tags: ['productivity', 'remote', 'work-life balance']
    },
    {
      id: '17',
      question: 'What tools do I need for remote work?',
      answer: 'Video conferencing (Zoom, Teams), project management (Asana, Trello), communication (Slack, Discord), and time tracking tools. Also ensure good internet and ergonomic setup.',
      category: 'Remote Work',
      tags: ['tools', 'technology', 'setup']
    },
    {
      id: '18',
      question: 'How do I manage work-life balance remotely?',
      answer: 'Set clear boundaries, establish routines, take regular breaks, communicate availability to family, and create physical separation between work and personal spaces.',
      category: 'Remote Work',
      tags: ['work-life balance', 'boundaries', 'routine']
    },
    {
      id: '19',
      question: 'How do I build relationships with remote colleagues?',
      answer: 'Participate in virtual team events, use video calls for casual conversations, join company chat channels, share personal updates, and be proactive in communication.',
      category: 'Remote Work',
      tags: ['relationships', 'team building', 'communication']
    },
    {
      id: '20',
      question: 'What are common remote work challenges?',
      answer: 'Isolation, distractions, communication barriers, time zone differences, technical issues, and difficulty separating work from personal life.',
      category: 'Remote Work',
      tags: ['challenges', 'problems', 'solutions']
    },
    // Technology & Skills
    {
      id: '21',
      question: 'What programming languages should I learn?',
      answer: 'Start with Python for beginners, JavaScript for web development, Java for enterprise, and consider learning SQL for data. Choose based on your career goals.',
      category: 'Technology',
      tags: ['programming', 'languages', 'coding']
    },
    {
      id: '22',
      question: 'How do I learn to code?',
      answer: 'Start with online platforms like Codecademy, freeCodeCamp, or Coursera. Practice with projects, join coding communities, and build a portfolio.',
      category: 'Technology',
      tags: ['learning', 'coding', 'programming']
    },
    {
      id: '23',
      question: 'What is machine learning?',
      answer: 'Machine learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed. It\'s used in recommendation systems, image recognition, and more.',
      category: 'Technology',
      tags: ['machine learning', 'ai', 'data science']
    },
    {
      id: '24',
      question: 'How do I improve my data analysis skills?',
      answer: 'Learn Excel, SQL, Python (pandas, numpy), and visualization tools like Tableau or Power BI. Practice with real datasets and take online courses.',
      category: 'Technology',
      tags: ['data analysis', 'skills', 'learning']
    },
    {
      id: '25',
      question: 'What is cloud computing?',
      answer: 'Cloud computing provides computing services over the internet. Major providers include AWS, Azure, and Google Cloud. It offers scalability, cost-effectiveness, and accessibility.',
      category: 'Technology',
      tags: ['cloud computing', 'aws', 'azure']
    },
    // Industry Specific
    {
      id: '26',
      question: 'How do I get into data science?',
      answer: 'Learn Python, statistics, machine learning, and data visualization. Build projects, participate in competitions like Kaggle, and gain experience through internships or freelance work.',
      category: 'Data Science',
      tags: ['data science', 'career path', 'skills']
    },
    {
      id: '27',
      question: 'What is UX/UI design?',
      answer: 'UX (User Experience) focuses on user research and usability, while UI (User Interface) deals with visual design. Both are crucial for creating user-friendly digital products.',
      category: 'Design',
      tags: ['ux', 'ui', 'design']
    },
    {
      id: '28',
      question: 'How do I become a product manager?',
      answer: 'Develop business acumen, learn product management tools, understand user research, gain technical knowledge, and start with associate or junior PM roles.',
      category: 'Product Management',
      tags: ['product management', 'career', 'leadership']
    },
    {
      id: '29',
      question: 'What is agile methodology?',
      answer: 'Agile is an iterative approach to project management that emphasizes flexibility, collaboration, and customer feedback. It includes frameworks like Scrum and Kanban.',
      category: 'Project Management',
      tags: ['agile', 'scrum', 'methodology']
    },
    {
      id: '30',
      question: 'How do I start freelancing?',
      answer: 'Identify your skills, create a portfolio, join platforms like Upwork or Fiverr, set competitive rates, build a client base, and maintain professional relationships.',
      category: 'Freelancing',
      tags: ['freelancing', 'self-employed', 'clients']
    }
  ];

  const categories = [
    { id: 'all', name: 'All Categories', icon: <FaBook /> },
    { id: 'Job Search', name: 'Job Search', icon: <FaSearch /> },
    { id: 'Interview', name: 'Interview', icon: <FaQuestionCircle /> },
    { id: 'Resume', name: 'Resume & CV', icon: <FaGraduationCap /> },
    { id: 'Remote Work', name: 'Remote Work', icon: <FaLightbulb /> },
    { id: 'Technology', name: 'Technology', icon: <FaLightbulb /> },
    { id: 'Career Change', name: 'Career Change', icon: <FaGraduationCap /> },
    { id: 'Salary', name: 'Salary & Benefits', icon: <FaBook /> },
    { id: 'Networking', name: 'Networking', icon: <FaSearch /> },
    { id: 'Skills', name: 'Skills Development', icon: <FaGraduationCap /> }
  ];

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    let filtered = qaData;

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(item => item.category === selectedCategory);
    }

    // Filter by search term
    if (searchTerm) {
      const lowerSearchTerm = searchTerm.toLowerCase();
      filtered = filtered.filter(item =>
        item.question.toLowerCase().includes(lowerSearchTerm) ||
        item.answer.toLowerCase().includes(lowerSearchTerm) ||
        item.tags.some(tag => tag.toLowerCase().includes(lowerSearchTerm))
      );
    }

    setFilteredQA(filtered);

    // Generate suggestions
    if (searchTerm.length > 2) {
      const allQuestions = qaData.map(item => item.question);
      const matchingQuestions = allQuestions.filter(question =>
        question.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setSuggestions(matchingQuestions.slice(0, 5));
      setShowSuggestions(true);
    } else {
      setShowSuggestions(false);
    }
  }, [searchTerm, selectedCategory]);

  const handleSuggestionClick = (suggestion: string) => {
    setSearchTerm(suggestion);
    setShowSuggestions(false);
  };

  const highlightText = (text: string, searchTerm: string) => {
    if (!searchTerm) return text;
    
    const regex = new RegExp(`(${searchTerm})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) =>
      regex.test(part) ? (
        <mark key={index} className="bg-yellow-200 px-1 rounded">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              Career Q&A Knowledge Base
            </h1>
            <p className="text-lg text-gray-600">
              Find answers to common career questions and job search advice
            </p>
          </div>

          {/* Search Bar */}
          <div className="mb-8" ref={searchRef}>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <FaSearch className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search questions, topics, or keywords..."
                className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Search Suggestions */}
            {showSuggestions && suggestions.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg">
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 focus:bg-gray-100 focus:outline-none"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Category Filters */}
          <div className="mb-8">
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    selectedCategory === category.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {category.icon}
                  {category.name}
                </button>
              ))}
            </div>
          </div>

          {/* Results Count */}
          <div className="mb-6">
            <p className="text-gray-600">
              {filteredQA.length} question{filteredQA.length !== 1 ? 's' : ''} found
              {searchTerm && ` for "${searchTerm}"`}
              {selectedCategory !== 'all' && ` in ${selectedCategory}`}
            </p>
          </div>

          {/* Q&A List */}
          <div className="space-y-6">
            {filteredQA.length === 0 ? (
              <div className="text-center py-12">
                <FaQuestionCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No questions found
                </h3>
                <p className="text-gray-600">
                  Try adjusting your search terms or browse different categories.
                </p>
              </div>
            ) : (
              filteredQA.map((item) => (
                <div
                  key={item.id}
                  className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {highlightText(item.question, searchTerm)}
                    </h3>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {item.category}
                    </span>
                  </div>
                  
                  <p className="text-gray-700 leading-relaxed">
                    {highlightText(item.answer, searchTerm)}
                  </p>
                  
                  <div className="mt-4 flex flex-wrap gap-2">
                    {item.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-700"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Load More */}
          {filteredQA.length > 0 && filteredQA.length < qaData.length && (
            <div className="text-center mt-8">
              <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                Load More Questions
              </button>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default QA; 
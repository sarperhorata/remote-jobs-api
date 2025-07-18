import React from 'react';
import Layout from '../components/Layout';
import { 
  Monitor, 
  Coffee, 
  Wifi, 
  Clock, 
  Users, 
  Calendar,
  Zap,
  Heart,
  Shield,
  Globe
} from 'lucide-react';

const RemoteTips: React.FC = () => {
  const tips = [
    {
      icon: <Monitor className="w-8 h-8 text-blue-500" />,
      title: "Set Up Your Workspace",
      description: "Create a dedicated, ergonomic workspace with proper lighting, comfortable seating, and minimal distractions.",
      tips: [
        "Invest in a good chair and desk",
        "Ensure proper lighting (natural light preferred)",
        "Keep your workspace clean and organized",
        "Add plants for a touch of nature"
      ]
    },
    {
      icon: <Coffee className="w-8 h-8 text-orange-500" />,
      title: "Establish Routines",
      description: "Create consistent daily routines to maintain productivity and work-life balance.",
      tips: [
        "Start and end work at the same time daily",
        "Take regular breaks (Pomodoro technique)",
        "Dress for work to get in the right mindset",
        "Plan your day the night before"
      ]
    },
    {
      icon: <Wifi className="w-8 h-8 text-green-500" />,
      title: "Optimize Your Tech Setup",
      description: "Ensure reliable internet and proper technology for seamless remote work.",
      tips: [
        "Get a high-speed internet connection",
        "Use a VPN for security",
        "Have backup equipment ready",
        "Test your setup regularly"
      ]
    },
    {
      icon: <Clock className="w-8 h-8 text-purple-500" />,
      title: "Time Management",
      description: "Master time management to stay productive and avoid burnout.",
      tips: [
        "Use time-tracking tools",
        "Set clear boundaries between work and personal time",
        "Prioritize tasks using the Eisenhower Matrix",
        "Learn to say no to unnecessary meetings"
      ]
    },
    {
      icon: <Users className="w-8 h-8 text-indigo-500" />,
      title: "Communication Skills",
      description: "Develop strong communication skills for effective remote collaboration.",
      tips: [
        "Over-communicate rather than under-communicate",
        "Use video calls for important discussions",
        "Write clear, concise messages",
        "Be proactive in reaching out to colleagues"
      ]
    },
    {
      icon: <Calendar className="w-8 h-8 text-red-500" />,
      title: "Work-Life Balance",
      description: "Maintain healthy boundaries between work and personal life.",
      tips: [
        "Set clear work hours and stick to them",
        "Take regular vacations and time off",
        "Separate your workspace from living space",
        "Practice self-care and mindfulness"
      ]
    }
  ];

  const productivityTools = [
    {
      name: "Time Tracking",
      tools: ["Toggl", "RescueTime", "Clockify", "Harvest"]
    },
    {
      name: "Project Management",
      tools: ["Notion", "Asana", "Trello", "Monday.com"]
    },
    {
      name: "Communication",
      tools: ["Slack", "Microsoft Teams", "Discord", "Zoom"]
    },
    {
      name: "Focus & Productivity",
      tools: ["Forest", "Freedom", "Cold Turkey", "Focus@Will"]
    }
  ];

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900">
        {/* Hero Section */}
        <div className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20"></div>
          <div className="relative container mx-auto px-4 py-16">
            <div className="text-center max-w-4xl mx-auto">
              <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
                Remote Work Tips & Tricks 🏠
              </h1>
              <p className="text-xl text-white/80 mb-8">
                Master the art of remote work with our comprehensive guide. 
                From setting up your workspace to maintaining work-life balance, 
                we've got you covered.
              </p>
              <div className="flex flex-wrap justify-center gap-4">
                <div className="bg-white/10 backdrop-blur-sm rounded-lg px-6 py-3 border border-white/20">
                  <span className="text-white font-semibold">500+ Tips</span>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-lg px-6 py-3 border border-white/20">
                  <span className="text-white font-semibold">Expert Advice</span>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-lg px-6 py-3 border border-white/20">
                  <span className="text-white font-semibold">Proven Strategies</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Tips Grid */}
        <div className="container mx-auto px-4 py-16">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {tips.map((tip, index) => (
              <div
                key={index}
                className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:bg-white/20 hover:border-white/30 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
              >
                <div className="flex items-center mb-4">
                  {tip.icon}
                  <h3 className="text-xl font-semibold text-white ml-3">
                    {tip.title}
                  </h3>
                </div>
                <p className="text-white/80 mb-4">
                  {tip.description}
                </p>
                <ul className="space-y-2">
                  {tip.tips.map((item, tipIndex) => (
                    <li key={tipIndex} className="flex items-start">
                      <Zap className="w-4 h-4 text-yellow-400 mt-0.5 mr-2 flex-shrink-0" />
                      <span className="text-white/70 text-sm">{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        {/* Productivity Tools Section */}
        <div className="container mx-auto px-4 py-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Essential Remote Work Tools 🛠️
            </h2>
            <p className="text-white/80 text-lg max-w-2xl mx-auto">
              Discover the best tools and apps that remote workers swear by for 
              productivity, communication, and work-life balance.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {productivityTools.map((category, index) => (
              <div
                key={index}
                className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-300"
              >
                <h3 className="text-lg font-semibold text-white mb-4">
                  {category.name}
                </h3>
                <div className="space-y-2">
                  {category.tools.map((tool, toolIndex) => (
                    <div
                      key={toolIndex}
                      className="bg-white/5 rounded-lg px-3 py-2 text-white/80 text-sm hover:bg-white/10 transition-colors cursor-pointer"
                    >
                      {tool}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Additional Tips Section */}
        <div className="container mx-auto px-4 py-16">
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-white mb-4">
                Pro Tips for Remote Success 💡
              </h2>
              <p className="text-white/80">
                Advanced strategies from experienced remote workers
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-4">
                <div className="flex items-start">
                  <Heart className="w-6 h-6 text-red-400 mt-1 mr-3 flex-shrink-0" />
                  <div>
                    <h4 className="text-white font-semibold mb-2">Build Relationships</h4>
                    <p className="text-white/70 text-sm">
                      Make time for virtual coffee chats and team building activities. 
                      Strong relationships are key to remote work success.
                    </p>
                  </div>
                </div>

                <div className="flex items-start">
                  <Shield className="w-6 h-6 text-blue-400 mt-1 mr-3 flex-shrink-0" />
                  <div>
                    <h4 className="text-white font-semibold mb-2">Cybersecurity First</h4>
                    <p className="text-white/70 text-sm">
                      Use strong passwords, enable 2FA, and keep your software updated. 
                      Your security is your responsibility.
                    </p>
                  </div>
                </div>

                <div className="flex items-start">
                  <Globe className="w-6 h-6 text-green-400 mt-1 mr-3 flex-shrink-0" />
                  <div>
                    <h4 className="text-white font-semibold mb-2">Embrace Flexibility</h4>
                    <p className="text-white/70 text-sm">
                      Remote work offers flexibility - use it wisely. 
                      Work when you're most productive, not just during traditional hours.
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-start">
                  <Zap className="w-6 h-6 text-yellow-400 mt-1 mr-3 flex-shrink-0" />
                  <div>
                    <h4 className="text-white font-semibold mb-2">Continuous Learning</h4>
                    <p className="text-white/70 text-sm">
                      Stay updated with remote work trends and tools. 
                      The remote work landscape is constantly evolving.
                    </p>
                  </div>
                </div>

                <div className="flex items-start">
                  <Users className="w-6 h-6 text-purple-400 mt-1 mr-3 flex-shrink-0" />
                  <div>
                    <h4 className="text-white font-semibold mb-2">Network Virtually</h4>
                    <p className="text-white/70 text-sm">
                      Join remote work communities and attend virtual events. 
                      Networking is still crucial for career growth.
                    </p>
                  </div>
                </div>

                <div className="flex items-start">
                  <Clock className="w-6 h-6 text-indigo-400 mt-1 mr-3 flex-shrink-0" />
                  <div>
                    <h4 className="text-white font-semibold mb-2">Time Zone Awareness</h4>
                    <p className="text-white/70 text-sm">
                      Be mindful of colleagues' time zones. 
                      Schedule meetings at reasonable hours for everyone involved.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="container mx-auto px-4 py-16">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-white mb-4">
              Ready to Find Your Remote Job? 🚀
            </h2>
            <p className="text-white/80 mb-8 max-w-2xl mx-auto">
              Now that you're equipped with remote work best practices, 
              start your journey to finding the perfect remote opportunity.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white font-semibold px-8 py-3 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200">
                Browse Remote Jobs
              </button>
              <button className="bg-white/10 backdrop-blur-sm border border-white/20 text-white font-semibold px-8 py-3 rounded-xl hover:bg-white/20 transition-all duration-200">
                Career Tips
              </button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default RemoteTips; 
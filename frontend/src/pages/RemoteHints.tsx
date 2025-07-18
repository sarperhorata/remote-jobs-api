import React from 'react';
import Layout from '../components/Layout';
import { 
  Lightbulb, 
  Clock, 
  Wifi, 
  Coffee, 
  Calendar, 
  Users, 
  Zap, 
  Target,
  CheckCircle,
  AlertCircle,
  Star,
  TrendingUp
} from 'lucide-react';

const RemoteHints: React.FC = () => {
  const productivityTips = [
    {
      icon: <Clock className="w-6 h-6" />,
      title: "Time Blocking",
      description: "Schedule specific time blocks for different tasks to maintain focus and avoid context switching.",
      category: "Productivity"
    },
    {
      icon: <Target className="w-6 h-6" />,
      title: "Daily Goals",
      description: "Set 3 main goals for each day and prioritize them over everything else.",
      category: "Productivity"
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Energy Management",
      description: "Work on complex tasks during your peak energy hours and save routine tasks for low-energy periods.",
      category: "Productivity"
    },
    {
      icon: <CheckCircle className="w-6 h-6" />,
      title: "Task Completion",
      description: "Finish one task completely before moving to the next to build momentum.",
      category: "Productivity"
    }
  ];

  const communicationTips = [
    {
      icon: <Users className="w-6 h-6" />,
      title: "Over-communicate",
      description: "In remote work, over-communication is better than under-communication. Keep your team updated.",
      category: "Communication"
    },
    {
      icon: <AlertCircle className="w-6 h-6" />,
      title: "Clear Expectations",
      description: "Always clarify deadlines, deliverables, and expectations to avoid misunderstandings.",
      category: "Communication"
    },
    {
      icon: <Star className="w-6 h-6" />,
      title: "Video Calls",
      description: "Use video calls for complex discussions and relationship building, not just text messages.",
      category: "Communication"
    },
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: "Regular Updates",
      description: "Provide regular status updates even when there's no major progress to report.",
      category: "Communication"
    }
  ];

  const workspaceTips = [
    {
      icon: <Wifi className="w-6 h-6" />,
      title: "Reliable Internet",
      description: "Invest in a good internet connection and have a backup plan for connectivity issues.",
      category: "Workspace"
    },
    {
      icon: <Coffee className="w-6 h-6" />,
      title: "Dedicated Space",
      description: "Create a dedicated workspace that's separate from your living area to maintain work-life balance.",
      category: "Workspace"
    },
    {
      icon: <Lightbulb className="w-6 h-6" />,
      title: "Good Lighting",
      description: "Ensure proper lighting to reduce eye strain and maintain professional appearance on video calls.",
      category: "Workspace"
    },
    {
      icon: <Calendar className="w-6 h-6" />,
      title: "Structured Schedule",
      description: "Maintain regular working hours and communicate your availability to your team.",
      category: "Workspace"
    }
  ];

  const quickHints = [
    "Use the Pomodoro Technique: 25 minutes of focused work followed by 5-minute breaks",
    "Keep your camera on during video calls to maintain human connection",
    "Take regular breaks to stretch and move around",
    "Use noise-canceling headphones to minimize distractions",
    "Set up automatic 'Do Not Disturb' during deep work sessions",
    "Create a morning routine to signal the start of your workday",
    "Use project management tools to track progress and deadlines",
    "Schedule virtual coffee chats with colleagues to maintain relationships",
    "Keep a work journal to track your achievements and challenges",
    "Set boundaries between work and personal time"
  ];

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        {/* Hero Section */}
        <div className="relative overflow-hidden bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-800 text-white py-20">
          <div className="absolute inset-0 bg-black/20"></div>
          <div className="relative container mx-auto px-4 text-center">
            <div className="max-w-4xl mx-auto">
              <h1 className="text-4xl md:text-6xl font-bold mb-6">
                Remote Work Hints 🚀
              </h1>
              <p className="text-xl md:text-2xl opacity-90 mb-8">
                Master the art of remote work with these proven tips and strategies
              </p>
              <div className="flex flex-wrap justify-center gap-4 text-sm">
                <span className="bg-white/20 px-3 py-1 rounded-full">Productivity</span>
                <span className="bg-white/20 px-3 py-1 rounded-full">Communication</span>
                <span className="bg-white/20 px-3 py-1 rounded-full">Workspace</span>
                <span className="bg-white/20 px-3 py-1 rounded-full">Work-Life Balance</span>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="container mx-auto px-4 py-16">
          {/* Productivity Tips */}
          <section className="mb-16">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                🎯 Productivity Hints
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Boost your remote work productivity with these proven strategies
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {productivityTips.map((tip, index) => (
                <div
                  key={index}
                  className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-200 border border-gray-100"
                >
                  <div className="text-blue-600 mb-4">{tip.icon}</div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{tip.title}</h3>
                  <p className="text-gray-600 text-sm">{tip.description}</p>
                </div>
              ))}
            </div>
          </section>

          {/* Communication Tips */}
          <section className="mb-16">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                💬 Communication Hints
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Master remote communication to stay connected with your team
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {communicationTips.map((tip, index) => (
                <div
                  key={index}
                  className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-200 border border-gray-100"
                >
                  <div className="text-green-600 mb-4">{tip.icon}</div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{tip.title}</h3>
                  <p className="text-gray-600 text-sm">{tip.description}</p>
                </div>
              ))}
            </div>
          </section>

          {/* Workspace Tips */}
          <section className="mb-16">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                🏠 Workspace Hints
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Create the perfect remote work environment
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {workspaceTips.map((tip, index) => (
                <div
                  key={index}
                  className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-200 border border-gray-100"
                >
                  <div className="text-purple-600 mb-4">{tip.icon}</div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{tip.title}</h3>
                  <p className="text-gray-600 text-sm">{tip.description}</p>
                </div>
              ))}
            </div>
          </section>

          {/* Quick Hints */}
          <section className="mb-16">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                ⚡ Quick Hints
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Simple tips you can implement right away
              </p>
            </div>
            
            <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-100">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {quickHints.map((hint, index) => (
                  <div
                    key={index}
                    className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                    <p className="text-gray-700">{hint}</p>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* Call to Action */}
          <section className="text-center">
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl p-8 text-white">
              <h3 className="text-2xl md:text-3xl font-bold mb-4">
                Ready to Level Up Your Remote Work?
              </h3>
              <p className="text-lg opacity-90 mb-6">
                Join thousands of professionals who've mastered remote work with Buzz2Remote
              </p>
              <button className="bg-white text-blue-600 font-semibold px-8 py-3 rounded-lg hover:bg-gray-100 transition-colors">
                Explore Remote Jobs
              </button>
            </div>
          </section>
        </div>
      </div>
    </Layout>
  );
};

export default RemoteHints; 
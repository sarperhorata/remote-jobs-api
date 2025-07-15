import React from 'react';
import Layout from '../components/Layout';
import { BookOpen, Users, Clock, Zap, Target, TrendingUp, Lightbulb, Award } from 'lucide-react';

const CareerTips: React.FC = () => {
  const tips = [
    {
      icon: <BookOpen className="w-6 h-6" />,
      title: "Remote Work Best Practices",
      content: "Learn how to maintain productivity, set boundaries, and create an effective home office environment.",
      tips: [
        "Create a dedicated workspace free from distractions",
        "Set clear work hours and communicate them to family/roommates",
        "Use time management techniques like Pomodoro",
        "Take regular breaks to avoid burnout",
        "Invest in ergonomic furniture and equipment"
      ]
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: "Building Professional Relationships",
      content: "Develop strong connections with colleagues and managers in a remote environment.",
      tips: [
        "Participate actively in team meetings and discussions",
        "Schedule regular 1-on-1s with your manager",
        "Join virtual team building activities",
        "Use video calls for important conversations",
        "Show appreciation and celebrate team successes"
      ]
    },
    {
      icon: <Clock className="w-6 h-6" />,
      title: "Time Management Skills",
      content: "Master the art of managing your time effectively in a remote setting.",
      tips: [
        "Use calendar blocking for focused work sessions",
        "Prioritize tasks using the Eisenhower Matrix",
        "Set realistic deadlines and communicate them",
        "Avoid multitasking - focus on one task at a time",
        "Review and adjust your schedule regularly"
      ]
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Staying Motivated",
      content: "Maintain high motivation and engagement while working remotely.",
      tips: [
        "Set clear goals and track your progress",
        "Create a morning routine to start your day right",
        "Dress professionally even when working from home",
        "Take advantage of flexible hours when possible",
        "Connect with colleagues for social interaction"
      ]
    },
    {
      icon: <Target className="w-6 h-6" />,
      title: "Career Advancement",
      content: "Strategies for advancing your career in a remote work environment.",
      tips: [
        "Take on additional responsibilities and projects",
        "Seek feedback regularly and act on it",
        "Develop new skills through online courses",
        "Build a strong online professional presence",
        "Network with industry professionals virtually"
      ]
    },
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: "Skill Development",
      content: "Continuously improve your skills to stay competitive in the remote job market.",
      tips: [
        "Identify in-demand skills in your industry",
        "Take online courses and certifications",
        "Practice new skills through side projects",
        "Join professional communities and forums",
        "Stay updated with industry trends and technologies"
      ]
    }
  ];

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-slate-900 via-blue-900 to-slate-900 bg-clip-text text-transparent mb-4">
              Career Tips & Advice
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Master the art of remote work with our comprehensive guide to building a successful career from anywhere in the world.
            </p>
          </div>

          {/* Tips Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
            {tips.map((tip, index) => (
              <div
                key={index}
                className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20 hover:shadow-xl transition-all duration-300 hover:scale-105"
              >
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl flex items-center justify-center text-white mr-4">
                    {tip.icon}
                  </div>
                  <h3 className="text-xl font-bold text-gray-900">{tip.title}</h3>
                </div>
                <p className="text-gray-600 mb-4">{tip.content}</p>
                <ul className="space-y-2">
                  {tip.tips.map((item, tipIndex) => (
                    <li key={tipIndex} className="flex items-start">
                      <Lightbulb className="w-4 h-4 text-yellow-500 mt-0.5 mr-2 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          {/* Call to Action */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-center text-white">
            <Award className="w-16 h-16 mx-auto mb-4 text-yellow-300" />
            <h2 className="text-3xl font-bold mb-4">Ready to Level Up Your Career?</h2>
            <p className="text-xl mb-6 opacity-90">
              Join thousands of remote professionals who are already using these strategies to advance their careers.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-white text-blue-600 font-semibold px-8 py-3 rounded-lg hover:bg-gray-100 transition-colors duration-200">
                Browse Remote Jobs
              </button>
              <button className="border-2 border-white text-white font-semibold px-8 py-3 rounded-lg hover:bg-white hover:text-blue-600 transition-colors duration-200">
                Create Profile
              </button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default CareerTips; 
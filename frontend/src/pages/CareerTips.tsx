import React from 'react';
import Layout from '../components/Layout';
import { 
  TrendingUp, 
  BookOpen, 
  Target, 
  Award, 
  MessageSquare, 
  Briefcase,
  Star,
  Lightbulb,
  Users,
  Calendar
} from 'lucide-react';

const CareerTips: React.FC = () => {
  const careerAreas = [
    {
      icon: <TrendingUp className="w-8 h-8 text-green-500" />,
      title: "Career Growth",
      description: "Strategies to advance your career and reach your professional goals.",
      tips: [
        "Set clear, measurable career goals",
        "Seek mentorship from experienced professionals",
        "Take on challenging projects outside your comfort zone",
        "Build a personal brand and online presence",
        "Continuously update your skills and knowledge"
      ]
    },
    {
      icon: <BookOpen className="w-8 h-8 text-blue-500" />,
      title: "Skill Development",
      description: "Essential skills for thriving in the modern remote work environment.",
      tips: [
        "Master digital communication tools",
        "Develop project management skills",
        "Learn data analysis and visualization",
        "Improve your writing and documentation skills",
        "Stay updated with industry trends and technologies"
      ]
    },
    {
      icon: <Target className="w-8 h-8 text-red-500" />,
      title: "Goal Setting",
      description: "How to set and achieve meaningful career objectives.",
      tips: [
        "Use SMART goal framework (Specific, Measurable, Achievable, Relevant, Time-bound)",
        "Break large goals into smaller, manageable tasks",
        "Regularly review and adjust your goals",
        "Celebrate small wins along the way",
        "Create accountability systems"
      ]
    },
    {
      icon: <Award className="w-8 h-8 text-yellow-500" />,
      title: "Personal Branding",
      description: "Build a strong professional reputation and online presence.",
      tips: [
        "Create a compelling LinkedIn profile",
        "Share your expertise through content creation",
        "Participate in industry discussions and forums",
        "Build a portfolio showcasing your work",
        "Network strategically both online and offline"
      ]
    },
    {
      icon: <MessageSquare className="w-8 h-8 text-purple-500" />,
      title: "Communication Skills",
      description: "Master the art of effective communication in remote settings.",
      tips: [
        "Practice active listening and empathy",
        "Write clear, concise, and professional emails",
        "Master video conferencing etiquette",
        "Give and receive constructive feedback",
        "Adapt communication style to different audiences"
      ]
    },
    {
      icon: <Briefcase className="w-8 h-8 text-indigo-500" />,
      title: "Job Search Strategy",
      description: "Effective strategies for finding and landing remote opportunities.",
      tips: [
        "Optimize your resume for ATS systems",
        "Tailor your cover letter for each application",
        "Build relationships with recruiters",
        "Prepare for remote interviews",
        "Follow up professionally after interviews"
      ]
    }
  ];

  const industryInsights = [
    {
      title: "Most In-Demand Remote Skills",
      skills: ["Python", "React", "Data Analysis", "Project Management", "Digital Marketing"]
    },
    {
      title: "Highest Paying Remote Roles",
      skills: ["Software Engineering", "Data Science", "Product Management", "DevOps", "UX Design"]
    },
    {
      title: "Emerging Remote Trends",
      skills: ["AI/ML", "Cybersecurity", "Cloud Computing", "Blockchain", "Sustainability"]
    },
    {
      title: "Soft Skills That Matter",
      skills: ["Adaptability", "Problem Solving", "Time Management", "Collaboration", "Leadership"]
    }
  ];

  const learningResources = [
    {
      category: "Online Courses",
      platforms: ["Coursera", "Udemy", "edX", "LinkedIn Learning", "Skillshare"]
    },
    {
      category: "Certifications",
      platforms: ["AWS", "Google Cloud", "Microsoft", "Cisco", "CompTIA"]
    },
    {
      category: "Free Resources",
      platforms: ["freeCodeCamp", "Khan Academy", "MIT OpenCourseWare", "YouTube", "GitHub"]
    },
    {
      category: "Professional Development",
      platforms: ["Toastmasters", "Industry Conferences", "Webinars", "Podcasts", "Books"]
    }
  ];

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900">
        {/* Hero Section */}
        <div className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-blue-600/20"></div>
          <div className="relative container mx-auto px-4 py-16">
            <div className="text-center max-w-4xl mx-auto">
              <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
                Career Development Guide 📈
              </h1>
              <p className="text-xl text-white/80 mb-8">
                Accelerate your career growth with expert advice, proven strategies, 
                and actionable tips for professional success in the remote work era.
              </p>
              <div className="flex flex-wrap justify-center gap-4">
                <div className="bg-white/10 backdrop-blur-sm rounded-lg px-6 py-3 border border-white/20">
                  <span className="text-white font-semibold">Expert Advice</span>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-lg px-6 py-3 border border-white/20">
                  <span className="text-white font-semibold">Proven Strategies</span>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-lg px-6 py-3 border border-white/20">
                  <span className="text-white font-semibold">Actionable Tips</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Career Areas Grid */}
        <div className="container mx-auto px-4 py-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Key Career Development Areas 🎯
            </h2>
            <p className="text-white/80 text-lg max-w-2xl mx-auto">
              Focus on these essential areas to accelerate your professional growth 
              and achieve your career goals.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {careerAreas.map((area, index) => (
              <div
                key={index}
                className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:bg-white/20 hover:border-white/30 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
              >
                <div className="flex items-center mb-4">
                  {area.icon}
                  <h3 className="text-xl font-semibold text-white ml-3">
                    {area.title}
                  </h3>
                </div>
                <p className="text-white/80 mb-4">
                  {area.description}
                </p>
                <ul className="space-y-2">
                  {area.tips.map((tip, tipIndex) => (
                    <li key={tipIndex} className="flex items-start">
                      <Star className="w-4 h-4 text-yellow-400 mt-0.5 mr-2 flex-shrink-0" />
                      <span className="text-white/70 text-sm">{tip}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        {/* Industry Insights */}
        <div className="container mx-auto px-4 py-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Industry Insights & Trends 📊
            </h2>
            <p className="text-white/80 text-lg max-w-2xl mx-auto">
              Stay ahead of the curve with the latest industry trends and in-demand skills.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {industryInsights.map((insight, index) => (
              <div
                key={index}
                className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-300"
              >
                <h3 className="text-lg font-semibold text-white mb-4">
                  {insight.title}
                </h3>
                <div className="space-y-2">
                  {insight.skills.map((skill, skillIndex) => (
                    <div
                      key={skillIndex}
                      className="bg-white/5 rounded-lg px-3 py-2 text-white/80 text-sm hover:bg-white/10 transition-colors cursor-pointer"
                    >
                      {skill}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Learning Resources */}
        <div className="container mx-auto px-4 py-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Learning Resources 📚
            </h2>
            <p className="text-white/80 text-lg max-w-2xl mx-auto">
              Discover the best platforms and resources to enhance your skills and knowledge.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {learningResources.map((resource, index) => (
              <div
                key={index}
                className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-300"
              >
                <h3 className="text-lg font-semibold text-white mb-4">
                  {resource.category}
                </h3>
                <div className="space-y-2">
                  {resource.platforms.map((platform, platformIndex) => (
                    <div
                      key={platformIndex}
                      className="bg-white/5 rounded-lg px-3 py-2 text-white/80 text-sm hover:bg-white/10 transition-colors cursor-pointer"
                    >
                      {platform}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Career Action Plan */}
        <div className="container mx-auto px-4 py-16">
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-white mb-4">
                Your 30-Day Career Action Plan 🚀
              </h2>
              <p className="text-white/80">
                A step-by-step guide to jumpstart your career development
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-4">
                <div className="flex items-start">
                  <Calendar className="w-6 h-6 text-blue-400 mt-1 mr-3 flex-shrink-0" />
                  <div>
                    <h4 className="text-white font-semibold mb-2">Week 1: Assessment</h4>
                    <p className="text-white/70 text-sm">
                      Evaluate your current skills, identify gaps, and set clear career goals. 
                      Update your resume and LinkedIn profile.
                    </p>
                  </div>
                </div>

                <div className="flex items-start">
                  <BookOpen className="w-6 h-6 text-green-400 mt-1 mr-3 flex-shrink-0" />
                  <div>
                    <h4 className="text-white font-semibold mb-2">Week 2: Learning</h4>
                    <p className="text-white/70 text-sm">
                      Enroll in relevant courses, start learning new skills, and begin building 
                      your professional network.
                    </p>
                  </div>
                </div>

                <div className="flex items-start">
                  <Users className="w-6 h-6 text-purple-400 mt-1 mr-3 flex-shrink-0" />
                  <div>
                    <h4 className="text-white font-semibold mb-2">Week 3: Networking</h4>
                    <p className="text-white/70 text-sm">
                      Attend industry events, join professional groups, and reach out to 
                      mentors and potential connections.
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-start">
                  <Target className="w-6 h-6 text-red-400 mt-1 mr-3 flex-shrink-0" />
                  <div>
                    <h4 className="text-white font-semibold mb-2">Week 4: Application</h4>
                    <p className="text-white/70 text-sm">
                      Apply for new opportunities, practice interviews, and showcase your 
                      newly acquired skills and knowledge.
                    </p>
                  </div>
                </div>

                <div className="flex items-start">
                  <Lightbulb className="w-6 h-6 text-yellow-400 mt-1 mr-3 flex-shrink-0" />
                  <div>
                    <h4 className="text-white font-semibold mb-2">Continuous Improvement</h4>
                    <p className="text-white/70 text-sm">
                      Make learning and skill development a lifelong habit. Stay curious, 
                      adapt to changes, and always be ready for new opportunities.
                    </p>
                  </div>
                </div>

                <div className="flex items-start">
                  <Award className="w-6 h-6 text-indigo-400 mt-1 mr-3 flex-shrink-0" />
                  <div>
                    <h4 className="text-white font-semibold mb-2">Celebrate Progress</h4>
                    <p className="text-white/70 text-sm">
                      Acknowledge your achievements, no matter how small. Track your progress 
                      and reward yourself for reaching milestones.
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
              Ready to Accelerate Your Career? 🎯
            </h2>
            <p className="text-white/80 mb-8 max-w-2xl mx-auto">
              Put these career tips into action and start your journey toward professional success. 
              Your dream career is waiting for you.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 text-white font-semibold px-8 py-3 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200">
                Find Remote Jobs
              </button>
              <button className="bg-white/10 backdrop-blur-sm border border-white/20 text-white font-semibold px-8 py-3 rounded-xl hover:bg-white/20 transition-all duration-200">
                Remote Work Tips
              </button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default CareerTips; 
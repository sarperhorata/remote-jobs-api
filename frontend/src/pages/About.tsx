import React from 'react';
import { Link } from 'react-router-dom';
import {
  Users,
  Globe,
  Target,
  Award,
  Heart,
  Zap,
  Shield,
  TrendingUp,
  CheckCircle,
  Star,
  MapPin,
  Calendar,
  Building,
  Rocket
} from 'lucide-react';
import Header from '../components/Header';
import Footer from '../components/Footer';

const About: React.FC = () => {
  const stats = [
    { icon: Users, value: '50K+', label: 'Job Seekers' },
    { icon: Building, value: '500+', label: 'Companies' },
    { icon: Globe, value: '100+', label: 'Countries' },
    { icon: CheckCircle, value: '10K+', label: 'Placements' }
  ];

  const values = [
    {
      icon: Heart,
      title: 'User-Centric',
      description: 'We put our users first, creating experiences that truly serve their needs.'
    },
    {
      icon: Shield,
      title: 'Trust & Security',
      description: 'Your data and privacy are our top priorities with enterprise-grade security.'
    },
    {
      icon: Zap,
      title: 'Innovation',
      description: 'Constantly evolving and improving to stay ahead of the remote work revolution.'
    },
    {
      icon: Globe,
      title: 'Global Reach',
      description: 'Connecting talent worldwide with opportunities that know no borders.'
    }
  ];

  const team = [
    {
      name: 'Sarah Johnson',
      role: 'CEO & Founder',
      image: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face',
      bio: 'Former remote worker turned entrepreneur, passionate about democratizing access to global opportunities.'
    },
    {
      name: 'Michael Chen',
      role: 'CTO',
      image: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
      bio: 'Tech leader with 15+ years building scalable platforms that connect millions of users.'
    },
    {
      name: 'Emma Rodriguez',
      role: 'Head of Product',
      image: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face',
      bio: 'Product strategist focused on creating intuitive experiences that make remote work seamless.'
    },
    {
      name: 'David Kim',
      role: 'Head of Growth',
      image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
      bio: 'Growth expert helping companies and talent find their perfect remote match.'
    }
  ];

  const milestones = [
    {
      year: '2024',
      title: 'Platform Launch',
      description: 'Buzz2Remote officially launched, connecting remote workers with global opportunities.'
    },
    {
      year: '2024',
      title: '10K Users',
      description: 'Reached our first 10,000 registered users within 6 months of launch.'
    },
    {
      year: '2024',
      title: '500+ Companies',
      description: 'Partnered with over 500 companies offering remote positions worldwide.'
    },
    {
      year: '2024',
      title: 'AI Integration',
      description: 'Launched AI-powered job matching and application optimization features.'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex flex-col">
      <Header />
      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative py-20 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/10"></div>
          <div className="relative container mx-auto px-4">
            <div className="text-center max-w-4xl mx-auto">
              <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-6">
                About Buzz2Remote
              </h1>
              <p className="text-xl text-gray-600 mb-8 leading-relaxed">
                We're revolutionizing the way people find remote work opportunities. 
                Our mission is to connect talented professionals with global companies, 
                making remote work accessible to everyone, everywhere.
              </p>
              <div className="flex flex-wrap justify-center gap-8">
                {stats.map((stat, index) => (
                  <div key={index} className="text-center">
                    <div className="flex items-center justify-center w-16 h-16 bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg mx-auto mb-3">
                      <stat.icon className="w-8 h-8 text-blue-600" />
                    </div>
                    <div className="text-3xl font-bold text-gray-800">{stat.value}</div>
                    <div className="text-gray-600">{stat.label}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Mission Section */}
        <section className="py-20 bg-white/50 backdrop-blur-sm">
          <div className="container mx-auto px-4">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="text-4xl font-bold text-gray-800 mb-6">
                  Our Mission
                </h2>
                <p className="text-lg text-gray-600 mb-6 leading-relaxed">
                  At Buzz2Remote, we believe that talent knows no geographical boundaries. 
                  Our mission is to break down the barriers that prevent talented individuals 
                  from accessing global opportunities, regardless of where they live.
                </p>
                <p className="text-lg text-gray-600 mb-8 leading-relaxed">
                  We're building the world's most comprehensive platform for remote work, 
                  connecting skilled professionals with forward-thinking companies that 
                  embrace the future of work.
                </p>
                <div className="flex items-center space-x-4">
                  <Target className="w-6 h-6 text-blue-600" />
                  <span className="text-gray-700 font-medium">Connecting Global Talent</span>
                </div>
              </div>
              <div className="relative">
                <div className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-3xl p-8 text-white">
                  <Rocket className="w-16 h-16 mb-6" />
                  <h3 className="text-2xl font-bold mb-4">The Future of Work</h3>
                  <p className="text-blue-100 leading-relaxed">
                    Remote work isn't just a trend—it's the future. We're here to make 
                    that future accessible to everyone, creating opportunities that 
                    transcend traditional workplace boundaries.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Values Section */}
        <section className="py-20">
          <div className="container mx-auto px-4">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-800 mb-4">Our Values</h2>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                The principles that guide everything we do at Buzz2Remote
              </p>
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
              {values.map((value, index) => (
                <div key={index} className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mb-4">
                    <value.icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-800 mb-3">{value.title}</h3>
                  <p className="text-gray-600 leading-relaxed">{value.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Team Section */}
        <section className="py-20 bg-white/50 backdrop-blur-sm">
          <div className="container mx-auto px-4">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-800 mb-4">Meet Our Team</h2>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                The passionate individuals behind Buzz2Remote's mission
              </p>
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
              {team.map((member, index) => (
                <div key={index} className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300">
                  <img 
                    src={member.image} 
                    alt={member.name}
                    className="w-24 h-24 rounded-full mx-auto mb-4 object-cover shadow-lg"
                  />
                  <h3 className="text-xl font-bold text-gray-800 text-center mb-1">{member.name}</h3>
                  <p className="text-blue-600 text-center mb-4 font-medium">{member.role}</p>
                  <p className="text-gray-600 text-center text-sm leading-relaxed">{member.bio}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Milestones Section */}
        <section className="py-20">
          <div className="container mx-auto px-4">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-800 mb-4">Our Journey</h2>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                Key milestones in our mission to democratize remote work
              </p>
            </div>
            <div className="relative">
              <div className="absolute left-1/2 transform -translate-x-px h-full w-0.5 bg-gradient-to-b from-blue-500 to-purple-600"></div>
              <div className="space-y-12">
                {milestones.map((milestone, index) => (
                  <div key={index} className={`relative flex items-center ${index % 2 === 0 ? 'flex-row' : 'flex-row-reverse'}`}>
                    <div className="w-1/2 px-8">
                      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg">
                        <div className="text-2xl font-bold text-blue-600 mb-2">{milestone.year}</div>
                        <h3 className="text-xl font-bold text-gray-800 mb-3">{milestone.title}</h3>
                        <p className="text-gray-600 leading-relaxed">{milestone.description}</p>
                      </div>
                    </div>
                    <div className="absolute left-1/2 transform -translate-x-1/2 w-4 h-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full shadow-lg"></div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-4xl font-bold text-white mb-6">
              Ready to join the remote revolution?
            </h2>
            <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
              Discover your next opportunity or find top remote talent with Buzz2Remote.
            </p>
            <Link
              to="/jobs"
              className="inline-block bg-white text-blue-600 font-semibold px-8 py-4 rounded-lg shadow-lg hover:bg-gray-100 transition-colors"
            >
              Browse Remote Jobs
            </Link>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
};

export default About; 
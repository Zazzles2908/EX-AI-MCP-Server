import React, { useState } from 'react';
import { Brain, Zap, Network, Play, MessageSquare, ArrowRight, Sparkles, Code, Bug, Shield, TrendingUp, Eye } from 'lucide-react';

const ExaiDemo = () => {
  const [userPrompt, setUserPrompt] = useState('');
  const [selectedMode, setSelectedMode] = useState(1);
  const [selectedTool, setSelectedTool] = useState('consensus');
  const [showInstructions, setShowInstructions] = useState(true);

  const modes = [
    { 
      name: 'Fast', 
      models: '1 model (glm-4.5-flash)',
      description: 'Quick single-model response',
      color: 'green',
      cost: '$0.003-0.008',
      useCase: 'Simple questions, quick iterations'
    },
    { 
      name: 'Smart', 
      models: '2 models (glm-4.6 + kimi-k2)',
      description: 'Dual model validation',
      color: 'blue',
      cost: '$0.008-0.015',
      useCase: 'Important decisions, code review'
    },
    { 
      name: 'Deep', 
      models: '3+ models with consensus',
      description: 'Full multi-model analysis',
      color: 'purple',
      cost: '$0.015-0.035',
      useCase: 'Critical systems, architecture decisions'
    }
  ];

  const tools = [
    {
      id: 'consensus',
      name: 'Consensus',
      icon: Network,
      description: 'Multiple models debate and synthesize insights',
      color: 'blue',
      examples: [
        'Should I use microservices or monolith for 50K users?',
        'Best authentication strategy: JWT vs sessions vs OAuth?',
        'Evaluate my product roadmap for Q1 2026'
      ],
      bestFor: 'Strategic decisions, architecture choices, debates'
    },
    {
      id: 'debug',
      name: 'Debug',
      icon: Bug,
      description: 'Step-by-step root cause analysis',
      color: 'red',
      examples: [
        'Python async race condition causing intermittent failures',
        'React component re-rendering too frequently',
        'Database query timeout in production only'
      ],
      bestFor: 'Bug hunting, performance issues, mysterious errors'
    },
    {
      id: 'analyze',
      name: 'Analyze',
      icon: Code,
      description: 'Comprehensive code/architecture assessment',
      color: 'purple',
      examples: [
        'Evaluate my MCP implementation architecture',
        'Assess technical debt in 15K LOC Python codebase',
        'Review scalability of my API design'
      ],
      bestFor: 'Code review, architecture assessment, tech debt audit'
    },
    {
      id: 'secaudit',
      name: 'Security Audit',
      icon: Shield,
      description: 'OWASP Top 10 + compliance analysis',
      color: 'orange',
      examples: [
        'Security audit my authentication flow',
        'Check for SQL injection vulnerabilities',
        'Validate GDPR compliance in data handling'
      ],
      bestFor: 'Security review, compliance validation, vulnerability scanning'
    },
    {
      id: 'chat',
      name: 'Chat',
      icon: MessageSquare,
      description: 'Collaborative thinking partner',
      color: 'green',
      examples: [
        'Help me design a distributed caching strategy',
        'Brainstorm ways to reduce API latency',
        'Explain WebSocket vs Server-Sent Events tradeoffs'
      ],
      bestFor: 'Brainstorming, explanations, collaborative problem-solving'
    }
  ];

  const generateCommand = () => {
    const tool = tools.find(t => t.id === selectedTool);
    const mode = modes[selectedMode];
    
    let command = `Claude, run EXAI ${tool.name} in ${mode.name} mode:\n\n`;
    command += `"${userPrompt || '[Your question here]'}"\n\n`;
    command += `Use models: ${mode.models}`;
    
    return command;
  };

  const quickPrompts = [
    {
      tool: 'consensus',
      prompt: 'Should I migrate from PostgreSQL to MongoDB for my 500K user SaaS app?',
      mode: 2
    },
    {
      tool: 'debug',
      prompt: 'My Express.js API returns 504 timeout only when handling concurrent uploads. Intermittent, happens ~30% of time.',
      mode: 1
    },
    {
      tool: 'analyze',
      prompt: 'Analyze my microservices architecture - is it over-engineered? 8 services, 50K users, 3-person team.',
      mode: 2
    },
    {
      tool: 'chat',
      prompt: 'I need to build a real-time notification system. Compare Firebase, WebSockets, and Server-Sent Events for my use case.',
      mode: 1
    }
  ];

  const loadQuickPrompt = (qp) => {
    setUserPrompt(qp.prompt);
    setSelectedTool(qp.tool);
    setSelectedMode(qp.mode);
    setShowInstructions(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Sparkles className="w-12 h-12 text-blue-400" />
            <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              EXAI Command Center
            </h1>
          </div>
          <p className="text-slate-300 text-xl">
            Multi-Model AI Orchestration - Now Actually Functional
          </p>
        </div>

        {/* How It Works */}
        {showInstructions && (
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-6 mb-6">
            <div className="flex items-start gap-4">
              <TrendingUp className="w-8 h-8 text-blue-400 flex-shrink-0 mt-1" />
              <div>
                <h2 className="text-xl font-bold mb-2">How This Actually Works</h2>
                <div className="grid md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <div className="font-semibold text-blue-300 mb-1">1. Configure</div>
                    <p className="text-slate-300">Choose tool, intelligence mode, write your prompt</p>
                  </div>
                  <div>
                    <div className="font-semibold text-blue-300 mb-1">2. Generate Command</div>
                    <p className="text-slate-300">Click "Generate" to create EXAI command</p>
                  </div>
                  <div>
                    <div className="font-semibold text-blue-300 mb-1">3. Execute</div>
                    <p className="text-slate-300">Copy command and send to Claude - real EXAI runs</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Quick Start Examples */}
        <div className="bg-slate-800/50 backdrop-blur rounded-xl p-6 mb-6 border border-slate-700">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5 text-yellow-400" />
            Quick Start Examples
          </h2>
          <div className="grid md:grid-cols-2 gap-3">
            {quickPrompts.map((qp, idx) => (
              <button
                key={idx}
                onClick={() => loadQuickPrompt(qp)}
                className="p-4 rounded-lg border border-slate-600 bg-slate-700/30 hover:bg-slate-700/60 transition-all text-left"
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs px-2 py-1 rounded bg-purple-500/30 font-mono">
                    {qp.tool}
                  </span>
                  <span className="text-xs px-2 py-1 rounded bg-blue-500/30">
                    {modes[qp.mode].name}
                  </span>
                </div>
                <p className="text-sm text-slate-300">{qp.prompt}</p>
              </button>
            ))}
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-6">
          {/* Tool Selection */}
          <div className="bg-slate-800/50 backdrop-blur rounded-xl p-6 border border-slate-700">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Brain className="w-5 h-5 text-purple-400" />
              Select EXAI Tool
            </h2>
            
            <div className="space-y-3">
              {tools.map((tool) => {
                const Icon = tool.icon;
                return (
                  <button
                    key={tool.id}
                    onClick={() => setSelectedTool(tool.id)}
                    className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                      selectedTool === tool.id
                        ? `border-${tool.color}-500 bg-${tool.color}-500/20`
                        : 'border-slate-700 bg-slate-800/30 hover:border-slate-600'
                    }`}
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <Icon className={`w-5 h-5 text-${tool.color}-400`} />
                      <h3 className="font-bold">{tool.name}</h3>
                    </div>
                    <p className="text-xs text-slate-400 mb-2">{tool.description}</p>
                    <p className="text-xs text-slate-500">Best for: {tool.bestFor}</p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Intelligence Mode */}
          <div className="bg-slate-800/50 backdrop-blur rounded-xl p-6 border border-slate-700">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-400" />
              Intelligence Mode
            </h2>

            <div className="flex items-center gap-4 mb-6">
              <input
                type="range"
                min="0"
                max="2"
                value={selectedMode}
                onChange={(e) => setSelectedMode(parseInt(e.target.value))}
                className="flex-1 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            <div className="space-y-3">
              {modes.map((mode, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    selectedMode === idx
                      ? `border-${mode.color}-500 bg-${mode.color}-500/20`
                      : 'border-slate-700 bg-slate-800/20'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-bold">{mode.name}</h3>
                    <span className="text-xs text-slate-400">{mode.cost}</span>
                  </div>
                  <p className="text-xs text-slate-400 mb-1">{mode.description}</p>
                  <p className="text-xs text-slate-500">Models: {mode.models}</p>
                  <p className="text-xs text-slate-500 mt-1">Use for: {mode.useCase}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Prompt Input */}
        <div className="bg-slate-800/50 backdrop-blur rounded-xl p-6 mb-6 border border-slate-700">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-green-400" />
            Your Question / Problem
          </h2>

          <textarea
            value={userPrompt}
            onChange={(e) => setUserPrompt(e.target.value)}
            placeholder={tools.find(t => t.id === selectedTool)?.examples[0] || "Enter your question, problem, or task..."}
            className="w-full h-32 bg-slate-900/50 border border-slate-600 rounded-lg p-4 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
          />

          <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
            <p className="text-sm text-blue-300 mb-2">
              <strong>Tip:</strong> Be specific! Include:
            </p>
            <ul className="text-xs text-slate-400 space-y-1 ml-4">
              <li>• Context (team size, user count, current tech stack)</li>
              <li>• Constraints (budget, timeline, skills available)</li>
              <li>• What you've tried already (if debugging)</li>
              <li>• Your specific question or goal</li>
            </ul>
          </div>
        </div>

        {/* Generated Command */}
        <div className="bg-gradient-to-r from-slate-800 to-slate-700 rounded-xl p-6 border border-slate-600 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <Eye className="w-5 h-5 text-purple-400" />
              Generated EXAI Command
            </h2>
            <button
              onClick={() => {
                navigator.clipboard.writeText(generateCommand());
                alert('Command copied to clipboard!');
              }}
              className="px-4 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg text-sm font-semibold transition-colors"
            >
              Copy Command
            </button>
          </div>

          <pre className="bg-slate-900/80 border border-slate-600 rounded-lg p-4 text-sm overflow-x-auto">
            <code className="text-green-400">{generateCommand()}</code>
          </pre>

          <div className="mt-4 flex items-start gap-3 p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
            <ArrowRight className="w-5 h-5 text-purple-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm text-purple-300 font-semibold mb-1">Next Step:</p>
              <p className="text-sm text-slate-300">
                Copy the command above and send it to Claude in this chat. Claude will execute the EXAI tools 
                and return real multi-model analysis results.
              </p>
            </div>
          </div>
        </div>

        {/* Examples for Selected Tool */}
        {selectedTool && (
          <div className="bg-slate-800/50 backdrop-blur rounded-xl p-6 border border-slate-700">
            <h2 className="text-xl font-semibold mb-4">
              Example Prompts for {tools.find(t => t.id === selectedTool)?.name}
            </h2>
            <div className="space-y-2">
              {tools.find(t => t.id === selectedTool)?.examples.map((example, idx) => (
                <button
                  key={idx}
                  onClick={() => setUserPrompt(example)}
                  className="w-full p-3 rounded-lg border border-slate-600 bg-slate-700/30 hover:bg-slate-700/60 transition-all text-left text-sm"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ExaiDemo;
import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { API_URL } from '../../services/api';
import { Bot, Send, Sparkles, Shield } from 'lucide-react';

interface RooneyMessage {
    role: 'user' | 'rooney';
    text: string;
    grounded?: boolean;
    source_labels?: string[];
    refusal_reason?: string;
}

const SUGGESTIONS = [
    "Who is leading right now?",
    "What events are scheduled today?",
    "How many gold medals does CCMS have?",
    "Are there any live matches currently?",
];

export default function Rooney() {
    const [messages, setMessages] = useState<RooneyMessage[]>([
        {
            role: 'rooney',
            text: "Hi! I'm Rooney, your official MSEUF intramurals assistant. Ask me about schedules, standings, and results — grounded in live data.",
            grounded: true,
            source_labels: [],
        }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const sendQuestion = async (question: string) => {
        if (!question.trim() || loading) return;

        const userMsg: RooneyMessage = { role: 'user', text: question };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const { data } = await axios.post(`${API_URL}/public/rooney/query/`, { question });
            const rooneyMsg: RooneyMessage = {
                role: 'rooney',
                text: data.grounded ? data.answer_text : '',
                grounded: data.grounded,
                source_labels: data.source_labels || [],
                refusal_reason: data.refusal_reason || '',
            };
            setMessages(prev => [...prev, rooneyMsg]);
        } catch {
            setMessages(prev => [...prev, {
                role: 'rooney',
                text: '',
                grounded: false,
                refusal_reason: 'Connection error. Please try again.',
            }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="py-8 max-w-3xl mx-auto flex flex-col" style={{ height: 'calc(100vh - 120px)' }}>
            {/* Header */}
            <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-full bg-maroon flex items-center justify-center shadow-md">
                    <Bot className="w-6 h-6 text-white" />
                </div>
                <div>
                    <h1 className="text-2xl font-black text-maroon">Rooney AI</h1>
                    <p className="text-xs text-gray-500 flex items-center gap-1">
                        <Shield className="w-3 h-3"/> Answers grounded in live Enverga Arena data only
                    </p>
                </div>
                <div className="ml-auto badge badge-success text-white gap-1">
                    <Sparkles className="w-3 h-3"/> Gemini 2.0
                </div>
            </div>

            {/* Chat window */}
            <div className="flex-1 overflow-y-auto space-y-4 bg-base-100 rounded-2xl border border-base-200 p-4 shadow-inner">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        {msg.role === 'rooney' && (
                            <div className="w-8 h-8 rounded-full bg-maroon flex items-center justify-center mr-2 mt-1 shrink-0">
                                <Bot className="w-4 h-4 text-white" />
                            </div>
                        )}
                        <div className={`max-w-sm rounded-2xl px-4 py-3 shadow-sm ${
                            msg.role === 'user'
                                ? 'bg-maroon text-white rounded-br-none'
                                : 'bg-base-200 text-charcoal rounded-bl-none'
                        }`}>
                            {msg.role === 'rooney' && !msg.grounded && msg.refusal_reason ? (
                                <p className="text-sm italic text-red-500">{msg.refusal_reason}</p>
                            ) : (
                                <p className="text-sm leading-relaxed">{msg.text}</p>
                            )}
                            {msg.role === 'rooney' && msg.source_labels && msg.source_labels.length > 0 && (
                                <div className="flex flex-wrap gap-1 mt-2">
                                    {msg.source_labels.map(label => (
                                        <span key={label} className="badge badge-outline badge-sm text-gray-500">
                                            {label}
                                        </span>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex justify-start">
                        <div className="w-8 h-8 rounded-full bg-maroon flex items-center justify-center mr-2 shrink-0">
                            <Bot className="w-4 h-4 text-white" />
                        </div>
                        <div className="bg-base-200 rounded-2xl rounded-bl-none px-4 py-3">
                            <span className="loading loading-dots loading-sm text-maroon"></span>
                        </div>
                    </div>
                )}
                <div ref={bottomRef} />
            </div>

            {/* Suggestions */}
            {messages.length <= 1 && (
                <div className="flex flex-wrap gap-2 mt-4">
                    {SUGGESTIONS.map(s => (
                        <button
                            key={s}
                            onClick={() => sendQuestion(s)}
                            className="btn btn-sm btn-outline border-maroon text-maroon hover:bg-maroon hover:text-white text-xs"
                        >
                            {s}
                        </button>
                    ))}
                </div>
            )}

            {/* Input */}
            <form
                className="flex gap-2 mt-4"
                onSubmit={e => { e.preventDefault(); sendQuestion(input); }}
            >
                <input
                    type="text"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    placeholder="Ask Rooney about schedules, results, or standings..."
                    className="input input-bordered flex-1 focus:outline-maroon"
                    disabled={loading}
                />
                <button
                    type="submit"
                    className="btn btn-square bg-maroon hover:bg-maroon-dark text-white border-none"
                    disabled={loading || !input.trim()}
                >
                    <Send className="w-5 h-5" />
                </button>
            </form>
        </div>
    );
}

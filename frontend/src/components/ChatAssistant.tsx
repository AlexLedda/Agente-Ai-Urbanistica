import { useState, useRef, useEffect } from 'react';
import { Send, Bot, FileText, Loader2, MapPin, ChevronDown, ChevronUp } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import LocationSelector from './LocationSelector';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    sources?: Array<{
        filename: string;
        page: number;
        content_preview: string;
    }>;
}

interface ChatAssistantProps {
    initialContext?: {
        region?: string;
        province?: string;
        municipality?: string;
    };
}

export const ChatAssistant = ({ initialContext }: ChatAssistantProps) => {
    const { token } = useAuth();
    const [messages, setMessages] = useState<Message[]>([
        {
            id: 'welcome',
            role: 'assistant',
            content: 'Ciao! Sono il tuo assistente urbanistico. Puoi farmi domande sulle normative caricate.'
        }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Location context state
    const [isContextOpen, setIsContextOpen] = useState(false);
    const [selectedLocation, setSelectedLocation] = useState({
        region: '',
        province: '',
        municipality: '',
        normative_level: ''
    });

    // Initialize context if provided
    useEffect(() => {
        if (initialContext) {
            setSelectedLocation(prev => ({
                ...prev,
                ...initialContext,
                normative_level: initialContext.municipality ? 'comunale' : initialContext.region ? 'regionale' : ''
            }));

            // Auto-send welcome for location
            if (initialContext.municipality) {
                setMessages(prev => [
                    ...prev,
                    {
                        id: Date.now().toString(),
                        role: 'assistant',
                        content: `Ho impostato il contesto su **${initialContext.municipality}**. Chiedimi pure le normative specifiche!`
                    }
                ]);
            }
        }
    }, [initialContext]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMsg: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input
        };

        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        try {
            const body = {
                message: userMsg.content,
                history: messages.map(m => ({ role: m.role, content: m.content })),
                // Add context
                region: selectedLocation.region || undefined,
                province: selectedLocation.province || undefined,
                municipality: selectedLocation.municipality || undefined
            };

            const response = await fetch('/api/chat/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(body)
            });

            if (!response.ok) {
                throw new Error('Errore nella comunicazione con il server');
            }

            const data = await response.json();

            const botMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.response,
                sources: data.sources
            };

            setMessages(prev => [...prev, botMsg]);

        } catch (error) {
            console.error(error);
            const errorMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: "Mi dispiace, si è verificato un errore. Riprova più tardi."
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-[600px] w-full max-w-4xl mx-auto glass-card overflow-hidden">
            {/* Header */}
            <div className="bg-gray-900/50 backdrop-blur-sm border-b border-gray-700/50">
                <div className="px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center">
                        <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center mr-4 shadow-lg shadow-primary/10">
                            <Bot className="w-6 h-6 text-primary" />
                        </div>
                        <div>
                            <h2 className="text-lg font-bold text-white">Assistente Urbanistico</h2>
                            <p className="text-xs text-green-400 flex items-center">
                                <span className="w-2 h-2 rounded-full bg-green-500 mr-2 animate-pulse"></span>
                                Online
                            </p>
                        </div>
                    </div>

                    <button
                        onClick={() => setIsContextOpen(!isContextOpen)}
                        className={`flex items-center text-xs px-3 py-1.5 rounded-lg border transition-all duration-300 ${isContextOpen
                            ? 'bg-primary/20 border-primary/50 text-white'
                            : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10'
                            }`}
                    >
                        <MapPin size={14} className="mr-1.5" />
                        {selectedLocation.municipality || selectedLocation.region || "Imposta Contesto"}
                        {isContextOpen ? <ChevronUp size={14} className="ml-1.5" /> : <ChevronDown size={14} className="ml-1.5" />}
                    </button>
                </div>

                {/* Collapsible Context Selector */}
                {isContextOpen && (
                    <div className="px-6 pb-4 bg-gray-900/80 border-b border-gray-700/50 animate-in slide-in-from-top-2 duration-200">
                        <div className="bg-gray-800/50 rounded-lg p-1 border border-gray-700/50">
                            <LocationSelector
                                onLocationSelect={setSelectedLocation}
                                initialSelection={initialContext}
                            />
                        </div>
                    </div>
                )}
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent">
                {messages.map((msg) => (
                    <div
                        key={msg.id}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`max-w-[85%] rounded-2xl p-4 shadow-md ${msg.role === 'user'
                                ? 'bg-primary text-white rounded-br-sm'
                                : 'bg-gray-700/50 backdrop-blur-sm border border-gray-600/50 text-gray-100 rounded-bl-sm'
                                }`}
                        >
                            <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>

                            {/* Sources */}
                            {msg.sources && msg.sources.length > 0 && (
                                <div className="mt-4 pt-3 border-t border-white/10 space-y-2">
                                    <p className="text-xs font-semibold opacity-70 mb-2 flex items-center">
                                        <FileText className="w-3 h-3 mr-1" /> Fonti Rilevate:
                                    </p>
                                    {msg.sources.map((src, idx) => (
                                        <div key={idx} className="text-xs bg-black/20 p-2.5 rounded hover:bg-black/30 transition-colors">
                                            <p className="font-medium text-blue-200">{src.filename} <span className="opacity-70">(pag. {src.page})</span></p>
                                            <p className="opacity-70 truncate italic mt-1 border-l-2 border-blue-400/50 pl-2">"{src.content_preview}"</p>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-gray-700/50 backdrop-blur-sm border border-gray-600/50 rounded-2xl rounded-bl-sm p-4 flex items-center space-x-3">
                            <Loader2 className="w-4 h-4 animate-spin text-primary" />
                            <span className="text-sm text-gray-300">Sto analizzando le normative...</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 bg-gray-900/50 backdrop-blur-sm border-t border-gray-700/50">
                <div className="flex items-center space-x-4">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Chiedi qualcosa sulle normative..."
                        className="glass-input flex-1 py-3 text-sm md:text-base"
                        disabled={isLoading}
                    />
                    <button
                        onClick={handleSend}
                        disabled={isLoading || !input.trim()}
                        className="bg-primary hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed text-white p-3 rounded-xl transition-all shadow-lg shadow-primary/20 hover:shadow-primary/40 active:scale-95"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    );
};

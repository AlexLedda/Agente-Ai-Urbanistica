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

export const ChatAssistant = () => {
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
        <div className="flex flex-col h-[600px] w-full max-w-4xl mx-auto bg-gray-800 rounded-xl border border-gray-700 overflow-hidden shadow-2xl">
            {/* Header */}
            <div className="bg-gray-900 border-b border-gray-700">
                <div className="px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center">
                        <div className="w-10 h-10 rounded-full bg-blue-600/20 flex items-center justify-center mr-4">
                            <Bot className="w-6 h-6 text-blue-400" />
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
                        className={`flex items-center text-xs px-3 py-1.5 rounded-lg border transition-colors ${isContextOpen
                                ? 'bg-blue-600/20 border-blue-500/50 text-blue-300'
                                : 'bg-gray-800 border-gray-700 text-gray-400 hover:bg-gray-700'
                            }`}
                    >
                        <MapPin size={14} className="mr-1.5" />
                        {selectedLocation.municipality || selectedLocation.region || "Imposta Contesto"}
                        {isContextOpen ? <ChevronUp size={14} className="ml-1.5" /> : <ChevronDown size={14} className="ml-1.5" />}
                    </button>
                </div>

                {/* Collapsible Context Selector */}
                {isContextOpen && (
                    <div className="px-6 pb-4 bg-gray-900 border-b border-gray-700 animate-in slide-in-from-top-2 duration-200">
                        <div className="bg-gray-800 rounded-lg p-1">
                            <LocationSelector onLocationSelect={setSelectedLocation} />
                        </div>
                    </div>
                )}
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gray-900/50">
                {messages.map((msg) => (
                    <div
                        key={msg.id}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`max-w-[80%] rounded-2xl p-4 ${msg.role === 'user'
                                ? 'bg-blue-600 text-white rounded-br-none'
                                : 'bg-gray-700 text-gray-100 rounded-bl-none'
                                }`}
                        >
                            <p className="whitespace-pre-wrap">{msg.content}</p>

                            {/* Sources */}
                            {msg.sources && msg.sources.length > 0 && (
                                <div className="mt-4 pt-4 border-t border-white/10 space-y-2">
                                    <p className="text-xs font-semibold opacity-70 mb-2 flex items-center">
                                        <FileText className="w-3 h-3 mr-1" /> Fonti Rilevate:
                                    </p>
                                    {msg.sources.map((src, idx) => (
                                        <div key={idx} className="text-xs bg-black/20 p-2 rounded">
                                            <p className="font-medium text-blue-300">{src.filename} (p. {src.page})</p>
                                            <p className="opacity-70 truncate italic mt-1">"{src.content_preview}"</p>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-gray-700 rounded-2xl rounded-bl-none p-4 flex items-center space-x-2">
                            <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
                            <span className="text-sm text-gray-400">Sto analizzando le normative...</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 bg-gray-800 border-t border-gray-700">
                <div className="flex items-center space-x-4">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Chiedi qualcosa sulle normative..."
                        className="flex-1 bg-gray-900 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-700 placeholder-gray-500"
                        disabled={isLoading}
                    />
                    <button
                        onClick={handleSend}
                        disabled={isLoading || !input.trim()}
                        className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white p-3 rounded-xl transition-colors"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    );
};

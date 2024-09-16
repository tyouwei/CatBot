'use client'

import { useState } from 'react'
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Send } from "lucide-react"

interface Message {
  id: number
  content: string
  sender: 'user' | 'bot'
}

export default function ChatbotUI() {
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, content: "Hello! How can I assist you today?", sender: 'bot' },
  ])
  const [input, setInput] = useState('')
  const [image, setImage] = useState('')

  const handleSend = async () => {
    if (input.trim()) {
      setMessages(prev => [...prev, { id: Date.now(), content: input, sender: 'user' }]);
      setInput('');
  
      try {
        console.log("Sending request to server...");
        const response = await fetch('http://localhost:5000/process', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ input })
        });
  
        // Check if the response is ok
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
  
        const data = await response.json();
        console.log("Received response from server:", data);
        const botMessage = data.response;

        if (botMessage.has_image) {
          setImage(botMessage.image_url);
        }

        const botReply = botMessage.message;
  
        setMessages(prev => [...prev, { id: Date.now(), content: botReply, sender: 'bot' }]);
      } catch (error) {
        console.error('Error sending message:', error);
      }
    }
  };
  

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="p-0">
        <div className="relative h-48 overflow-hidden rounded-t-lg">
          <img
            src={image}
            alt="Chatbot header image"
            className="w-full h-full object-cover"
          />
        </div>
      </CardHeader>
      <CardContent className="p-4">
        <ScrollArea className="h-[400px] pr-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} mb-4`}
            >
              {message.sender === 'bot' && (
                <Avatar className="mr-2">
                  <AvatarImage src="/placeholder.svg?height=40&width=40" alt="Bot Avatar" />
                  <AvatarFallback>Bot</AvatarFallback>
                </Avatar>
              )}
              <div
                className={`rounded-lg p-3 max-w-[70%] ${
                  message.sender === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted'
                }`}
              >
                {message.content}
              </div>
              {message.sender === 'user' && (
                <Avatar className="ml-2">
                  <AvatarImage src="/placeholder.svg?height=40&width=40" alt="User Avatar" />
                  <AvatarFallback>You</AvatarFallback>
                </Avatar>
              )}
            </div>
          ))}
        </ScrollArea>
      </CardContent>
      <CardFooter className="p-4 pt-0">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleSend()
          }}
          className="flex w-full items-center space-x-2"
        >
          <Input
            type="text"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <Button type="submit" size="icon">
            <Send className="h-4 w-4" />
            <span className="sr-only">Send</span>
          </Button>
        </form>
      </CardFooter>
    </Card>
  )
}
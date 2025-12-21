import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { History, User, ArrowRight, Calendar, RefreshCw } from 'lucide-react';
import { toast } from '@/components/ui/use-toast';
import api from '@/services/api';

interface AssignmentHistoryEntry {
  id: string;
  assignment_id?: string;
  entity_type: string;
  entity_id: string;
  user_id: string;
  assignment_type: string;
  action: string;
  previous_user_id?: string;
  created_at: string;
  user_name?: string;
  previous_user_name?: string;
}

interface AssignmentHistoryProps {
  entityType: string;
  entityId: string;
  maxEntries?: number;
}

export const AssignmentHistory: React.FC<AssignmentHistoryProps> = ({
  entityType,
  entityId,
  maxEntries = 10
}) => {
  const [history, setHistory] = useState<AssignmentHistoryEntry[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadHistory();
  }, [entityType, entityId]);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/assignments/history/${entityType}/${entityId}`);
      setHistory(response.data.slice(0, maxEntries));
    } catch (error) {
      console.error('Failed to load assignment history:', error);
      toast({
        title: 'Error',
        description: 'Failed to load assignment history',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case 'assigned':
        return 'bg-green-100 text-green-800';
      case 'unassigned':
        return 'bg-red-100 text-red-800';
      case 'reassigned':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'assigned':
        return <User className="w-4 h-4" />;
      case 'unassigned':
        return <User className="w-4 h-4" />;
      case 'reassigned':
        return <ArrowRight className="w-4 h-4" />;
      default:
        return <RefreshCw className="w-4 h-4" />;
    }
  };

  const getInitials = (name?: string) => {
    if (!name) return '?';
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return {
      date: date.toLocaleDateString(),
      time: date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
  };

  const getAssignmentTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      'owner': 'Owner',
      'contact_person': 'Contact Person',
      'developer': 'Developer'
    };
    return labels[type] || type;
  };

  const renderHistoryEntry = (entry: AssignmentHistoryEntry) => {
    const { date, time } = formatDate(entry.created_at);
    
    return (
      <div key={entry.id} className="flex items-start space-x-3 p-3 border rounded-lg">
        <div className={`p-2 rounded-full ${getActionColor(entry.action)}`}>
          {getActionIcon(entry.action)}
        </div>
        
        <div className="flex-1 space-y-2">
          <div className="flex items-center justify-between">
            <Badge variant="outline" className="text-xs">
              {getAssignmentTypeLabel(entry.assignment_type)}
            </Badge>
            <div className="flex items-center text-xs text-muted-foreground">
              <Calendar className="w-3 h-3 mr-1" />
              {date} at {time}
            </div>
          </div>
          
          <div className="text-sm">
            {entry.action === 'assigned' && (
              <div className="flex items-center space-x-2">
                <span>Assigned to</span>
                <Avatar className="w-6 h-6">
                  <AvatarFallback className="text-xs">
                    {getInitials(entry.user_name)}
                  </AvatarFallback>
                </Avatar>
                <span className="font-medium">{entry.user_name}</span>
              </div>
            )}
            
            {entry.action === 'unassigned' && (
              <div className="flex items-center space-x-2">
                <span>Unassigned from</span>
                <Avatar className="w-6 h-6">
                  <AvatarFallback className="text-xs">
                    {getInitials(entry.user_name)}
                  </AvatarFallback>
                </Avatar>
                <span className="font-medium">{entry.user_name}</span>
              </div>
            )}
            
            {entry.action === 'reassigned' && (
              <div className="flex items-center space-x-2">
                <span>Reassigned from</span>
                <Avatar className="w-6 h-6">
                  <AvatarFallback className="text-xs">
                    {getInitials(entry.previous_user_name)}
                  </AvatarFallback>
                </Avatar>
                <span className="font-medium">{entry.previous_user_name}</span>
                <ArrowRight className="w-4 h-4 text-muted-foreground" />
                <Avatar className="w-6 h-6">
                  <AvatarFallback className="text-xs">
                    {getInitials(entry.user_name)}
                  </AvatarFallback>
                </Avatar>
                <span className="font-medium">{entry.user_name}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center">Loading assignment history...</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center text-sm">
            <History className="w-4 h-4 mr-2" />
            Assignment History
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={loadHistory}>
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {history.length === 0 ? (
          <div className="text-center py-4 text-muted-foreground text-sm">
            No assignment history found
          </div>
        ) : (
          <div className="space-y-3">
            {history.map(renderHistoryEntry)}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
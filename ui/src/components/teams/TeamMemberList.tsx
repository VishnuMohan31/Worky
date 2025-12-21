import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { UserPlus, Trash2, Edit, Mail, Calendar } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { toast } from '@/components/ui/use-toast';
import api from '@/services/api';

interface TeamMember {
  id: string;
  user_id: string;
  role: string;
  user_name?: string;
  user_email?: string;
  joined_at: string;
  is_active: boolean;
}

interface User {
  id: string;
  full_name: string;
  email: string;
  role: string;
}

interface TeamMemberListProps {
  teamId: string;
  projectId?: string;
  canManage?: boolean;
  onMemberChange?: () => void;
}

export const TeamMemberList: React.FC<TeamMemberListProps> = ({
  teamId,
  projectId,
  canManage = false,
  onMemberChange
}) => {
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [availableUsers, setAvailableUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState('');
  const [selectedRole, setSelectedRole] = useState('Developer');

  useEffect(() => {
    if (teamId) {
      loadMembers();
      if (canManage) {
        loadAvailableUsers();
      }
    }
  }, [teamId, canManage]);

  const loadMembers = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/teams/${teamId}/members`);
      setMembers(response.data);
    } catch (error) {
      console.error('Failed to load team members:', error);
      toast({
        title: 'Error',
        description: 'Failed to load team members',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const loadAvailableUsers = async () => {
    try {
      const response = await api.get('/users/');
      // Filter out users who are already team members
      const memberUserIds = members.map(m => m.user_id);
      const available = response.data.filter((user: User) => 
        !memberUserIds.includes(user.id)
      );
      setAvailableUsers(available);
    } catch (error) {
      console.error('Failed to load available users:', error);
    }
  };

  const handleAddMember = async () => {
    if (!selectedUserId) {
      toast({
        title: 'Error',
        description: 'Please select a user',
        variant: 'destructive'
      });
      return;
    }

    try {
      await api.post(`/teams/${teamId}/members`, {
        user_id: selectedUserId,
        role: selectedRole
      });

      toast({
        title: 'Success',
        description: 'Member added successfully'
      });

      setShowAddDialog(false);
      setSelectedUserId('');
      setSelectedRole('Developer');
      loadMembers();
      loadAvailableUsers();
      onMemberChange?.();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to add member',
        variant: 'destructive'
      });
    }
  };

  const handleRemoveMember = async (userId: string) => {
    try {
      await api.delete(`/teams/${teamId}/members/${userId}`);
      
      toast({
        title: 'Success',
        description: 'Member removed successfully'
      });

      loadMembers();
      loadAvailableUsers();
      onMemberChange?.();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to remove member',
        variant: 'destructive'
      });
    }
  };

  const getRoleColor = (role: string) => {
    switch (role.toLowerCase()) {
      case 'owner':
        return 'bg-red-100 text-red-800';
      case 'architect':
        return 'bg-purple-100 text-purple-800';
      case 'developer':
        return 'bg-blue-100 text-blue-800';
      case 'tester':
        return 'bg-green-100 text-green-800';
      case 'designer':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
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
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center">Loading team members...</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center">
            Team Members ({members.length})
          </CardTitle>
          {canManage && (
            <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
              <DialogTrigger asChild>
                <Button size="sm">
                  <UserPlus className="w-4 h-4 mr-2" />
                  Add Member
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Add Team Member</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label>User</Label>
                    <Select value={selectedUserId} onValueChange={setSelectedUserId}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select user" />
                      </SelectTrigger>
                      <SelectContent>
                        {availableUsers.map((user) => (
                          <SelectItem key={user.id} value={user.id}>
                            <div className="flex items-center">
                              <Avatar className="w-6 h-6 mr-2">
                                <AvatarFallback className="text-xs">
                                  {getInitials(user.full_name)}
                                </AvatarFallback>
                              </Avatar>
                              <div>
                                <div className="font-medium">{user.full_name}</div>
                                <div className="text-sm text-muted-foreground">{user.email}</div>
                              </div>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label>Role</Label>
                    <Select value={selectedRole} onValueChange={setSelectedRole}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Owner">Owner</SelectItem>
                        <SelectItem value="Architect">Architect</SelectItem>
                        <SelectItem value="Developer">Developer</SelectItem>
                        <SelectItem value="Tester">Tester</SelectItem>
                        <SelectItem value="Designer">Designer</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="flex justify-end space-x-2">
                    <Button variant="outline" onClick={() => setShowAddDialog(false)}>
                      Cancel
                    </Button>
                    <Button onClick={handleAddMember}>
                      Add Member
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {members.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            No team members found
          </div>
        ) : (
          <div className="space-y-3">
            {members.map((member) => (
              <div
                key={member.id}
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <Avatar>
                    <AvatarFallback>
                      {getInitials(member.user_name)}
                    </AvatarFallback>
                  </Avatar>
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h4 className="font-medium">{member.user_name || 'Unknown User'}</h4>
                      <Badge className={getRoleColor(member.role)}>
                        {member.role}
                      </Badge>
                    </div>
                    
                    <div className="flex items-center space-x-4 mt-1 text-sm text-muted-foreground">
                      {member.user_email && (
                        <div className="flex items-center">
                          <Mail className="w-3 h-3 mr-1" />
                          {member.user_email}
                        </div>
                      )}
                      <div className="flex items-center">
                        <Calendar className="w-3 h-3 mr-1" />
                        Joined {formatDate(member.joined_at)}
                      </div>
                    </div>
                  </div>
                </div>

                {canManage && (
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveMember(member.user_id)}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
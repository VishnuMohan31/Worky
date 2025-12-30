import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Plus, Users, Edit, Trash2, UserPlus } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/components/ui/use-toast';
import api from '@/services/api';

interface Team {
  id: string;
  name: string;
  description?: string;
  project_id: string;
  is_active: boolean;
  member_count: number;
  created_at: string;
  updated_at: string;
}

interface TeamMember {
  id: string;
  user_id: string;
  role: string;
  user_name?: string;
  user_email?: string;
  joined_at: string;
  is_active: boolean;
}

interface Project {
  id: string;
  name: string;
}

interface User {
  id: string;
  full_name: string;
  email: string;
  role: string;
}

interface TeamManagementProps {
  projectId?: string;
}

export const TeamManagement: React.FC<TeamManagementProps> = ({ projectId }) => {
  const [teams, setTeams] = useState<Team[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showAddMemberDialog, setShowAddMemberDialog] = useState(false);

  // Form states
  const [teamForm, setTeamForm] = useState({
    name: '',
    description: '',
    project_id: projectId || ''
  });

  const [memberForm, setMemberForm] = useState({
    user_id: '',
    role: 'Developer'
  });

  useEffect(() => {
    loadTeams();
    loadProjects();
    loadUsers();
  }, [projectId]);

  const loadTeams = async () => {
    try {
      setLoading(true);
      const params = projectId ? { project_id: projectId } : {};
      const response = await api.get('/teams/', { params });
      setTeams(response.data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load teams',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const loadProjects = async () => {
    try {
      const response = await api.get('/projects/');
      setProjects(response.data);
    } catch (error) {
      console.error('Failed to load projects:', error);
    }
  };

  const loadUsers = async () => {
    try {
      const response = await api.get('/users/');
      setUsers(response.data);
    } catch (error) {
      console.error('Failed to load users:', error);
    }
  };

  const loadTeamMembers = async (teamId: string) => {
    try {
      const response = await api.get(`/teams/${teamId}/members`);
      setTeamMembers(response.data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load team members',
        variant: 'destructive'
      });
    }
  };

  const handleCreateTeam = async () => {
    try {
      if (!teamForm.name || !teamForm.project_id) {
        toast({
          title: 'Error',
          description: 'Please fill in all required fields',
          variant: 'destructive'
        });
        return;
      }

      await api.post('/teams/', teamForm);
      
      toast({
        title: 'Success',
        description: 'Team created successfully'
      });

      setShowCreateDialog(false);
      setTeamForm({ name: '', description: '', project_id: projectId || '' });
      loadTeams();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create team',
        variant: 'destructive'
      });
    }
  };

  const handleAddMember = async () => {
    if (!selectedTeam || !memberForm.user_id) {
      toast({
        title: 'Error',
        description: 'Please select a user',
        variant: 'destructive'
      });
      return;
    }

    try {
      await api.post(`/teams/${selectedTeam.id}/members`, memberForm);
      
      toast({
        title: 'Success',
        description: 'Member added successfully'
      });

      setShowAddMemberDialog(false);
      setMemberForm({ user_id: '', role: 'Developer' });
      loadTeamMembers(selectedTeam.id);
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to add member',
        variant: 'destructive'
      });
    }
  };

  const handleRemoveMember = async (teamId: string, userId: string) => {
    try {
      await api.delete(`/teams/${teamId}/members/${userId}`);
      
      toast({
        title: 'Success',
        description: 'Member removed successfully'
      });

      loadTeamMembers(teamId);
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to remove member',
        variant: 'destructive'
      });
    }
  };

  const selectTeam = (team: Team) => {
    setSelectedTeam(team);
    loadTeamMembers(team.id);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Team Management</h2>
          <p className="text-muted-foreground">
            Manage project teams and team members
          </p>
        </div>
        
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Create Team
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Team</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="team-name">Team Name *</Label>
                <Input
                  id="team-name"
                  value={teamForm.name}
                  onChange={(e) => setTeamForm({ ...teamForm, name: e.target.value })}
                  placeholder="Enter team name"
                />
              </div>
              
              <div>
                <Label htmlFor="team-description">Description</Label>
                <Textarea
                  id="team-description"
                  value={teamForm.description}
                  onChange={(e) => setTeamForm({ ...teamForm, description: e.target.value })}
                  placeholder="Enter team description"
                />
              </div>
              
              {!projectId && (
                <div>
                  <Label htmlFor="team-project">Project *</Label>
                  <Select
                    value={teamForm.project_id}
                    onValueChange={(value) => setTeamForm({ ...teamForm, project_id: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select project" />
                    </SelectTrigger>
                    <SelectContent>
                      {projects.map((project) => (
                        <SelectItem key={project.id} value={project.id}>
                          {project.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
              
              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateTeam}>
                  Create Team
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Teams List */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Users className="w-5 h-5 mr-2" />
              Teams
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-4">Loading teams...</div>
            ) : teams.length === 0 ? (
              <div className="text-center py-4 text-muted-foreground">
                No teams found
              </div>
            ) : (
              <div className="space-y-2">
                {teams.map((team) => (
                  <div
                    key={team.id}
                    className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                      selectedTeam?.id === team.id
                        ? 'border-primary bg-primary/5'
                        : 'hover:bg-muted/50'
                    }`}
                    onClick={() => selectTeam(team)}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-medium">{team.name}</h4>
                        {team.description && (
                          <p className="text-sm text-muted-foreground mt-1">
                            {team.description}
                          </p>
                        )}
                      </div>
                      <Badge variant="secondary">
                        {team.member_count} members
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Team Members */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Team Members</span>
              {selectedTeam && (
                <Dialog open={showAddMemberDialog} onOpenChange={setShowAddMemberDialog}>
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
                        <Label htmlFor="member-user">User *</Label>
                        <Select
                          value={memberForm.user_id}
                          onValueChange={(value) => setMemberForm({ ...memberForm, user_id: value })}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select user" />
                          </SelectTrigger>
                          <SelectContent>
                            {users.map((user) => (
                              <SelectItem key={user.id} value={user.id}>
                                {user.full_name} ({user.email})
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div>
                        <Label htmlFor="member-role">Role</Label>
                        <Select
                          value={memberForm.role}
                          onValueChange={(value) => setMemberForm({ ...memberForm, role: value })}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="Owner">Owner</SelectItem>
                            <SelectItem value="Developer">Developer</SelectItem>
                            <SelectItem value="Tester">Tester</SelectItem>
                            <SelectItem value="Architect">Architect</SelectItem>
                            <SelectItem value="Designer">Designer</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div className="flex justify-end space-x-2">
                        <Button variant="outline" onClick={() => setShowAddMemberDialog(false)}>
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
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!selectedTeam ? (
              <div className="text-center py-4 text-muted-foreground">
                Select a team to view members
              </div>
            ) : teamMembers.length === 0 ? (
              <div className="text-center py-4 text-muted-foreground">
                No members in this team
              </div>
            ) : (
              <div className="space-y-2">
                {teamMembers.map((member) => (
                  <div
                    key={member.id}
                    className="flex items-center justify-between p-3 border rounded-lg"
                  >
                    <div>
                      <h4 className="font-medium">{member.user_name}</h4>
                      <p className="text-sm text-muted-foreground">{member.user_email}</p>
                      <Badge variant="outline" className="mt-1">
                        {member.role}
                      </Badge>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveMember(selectedTeam.id, member.user_id)}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
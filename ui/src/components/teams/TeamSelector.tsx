import React, { useState, useEffect } from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Users } from 'lucide-react';
import api from '@/services/api';

interface Team {
  id: string;
  name: string;
  description?: string;
  project_id: string;
  member_count: number;
}

interface TeamSelectorProps {
  projectId: string;
  value?: string;
  onValueChange: (teamId: string) => void;
  label?: string;
  placeholder?: string;
  disabled?: boolean;
}

export const TeamSelector: React.FC<TeamSelectorProps> = ({
  projectId,
  value,
  onValueChange,
  label = "Team",
  placeholder = "Select team",
  disabled = false
}) => {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (projectId) {
      loadTeams();
    }
  }, [projectId]);

  const loadTeams = async () => {
    try {
      setLoading(true);
      const response = await api.get('/teams/', {
        params: { project_id: projectId, is_active: true }
      });
      setTeams(response.data);
    } catch (error) {
      console.error('Failed to load teams:', error);
      setTeams([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-2">
      {label && <Label>{label}</Label>}
      <Select
        value={value}
        onValueChange={onValueChange}
        disabled={disabled || loading}
      >
        <SelectTrigger>
          <SelectValue placeholder={loading ? "Loading teams..." : placeholder} />
        </SelectTrigger>
        <SelectContent>
          {teams.map((team) => (
            <SelectItem key={team.id} value={team.id}>
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center">
                  <Users className="w-4 h-4 mr-2" />
                  <span>{team.name}</span>
                </div>
                <Badge variant="secondary" className="ml-2">
                  {team.member_count}
                </Badge>
              </div>
            </SelectItem>
          ))}
          {teams.length === 0 && !loading && (
            <SelectItem value="" disabled>
              No teams available
            </SelectItem>
          )}
        </SelectContent>
      </Select>
    </div>
  );
};
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Users, CheckCircle, XCircle, AlertCircle, Upload } from 'lucide-react';
import { toast } from '@/components/ui/use-toast';
import api from '@/services/api';

interface Entity {
  id: string;
  name: string;
  type: string;
  current_assignment?: string;
}

interface User {
  id: string;
  full_name: string;
  email: string;
  role: string;
}

interface BulkAssignmentResult {
  successful: Array<{
    assignment_id: string;
    entity_type: string;
    entity_id: string;
    user_id: string;
  }>;
  failed: Array<{
    entity_type: string;
    entity_id: string;
    user_id: string;
    error: string;
  }>;
  total: number;
}

interface BulkAssignmentProps {
  entities: Entity[];
  onAssignmentComplete?: (results: BulkAssignmentResult) => void;
}

export const BulkAssignment: React.FC<BulkAssignmentProps> = ({
  entities,
  onAssignmentComplete
}) => {
  const [selectedEntities, setSelectedEntities] = useState<string[]>([]);
  const [selectedUser, setSelectedUser] = useState('');
  const [assignmentType, setAssignmentType] = useState('developer');
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<BulkAssignmentResult | null>(null);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const response = await api.get('/users/');
      setUsers(response.data);
    } catch (error) {
      console.error('Failed to load users:', error);
      toast({
        title: 'Error',
        description: 'Failed to load users',
        variant: 'destructive'
      });
    }
  };

  const handleEntityToggle = (entityId: string) => {
    setSelectedEntities(prev => 
      prev.includes(entityId)
        ? prev.filter(id => id !== entityId)
        : [...prev, entityId]
    );
  };

  const handleSelectAll = () => {
    if (selectedEntities.length === entities.length) {
      setSelectedEntities([]);
    } else {
      setSelectedEntities(entities.map(e => e.id));
    }
  };

  const handleBulkAssign = async () => {
    if (selectedEntities.length === 0) {
      toast({
        title: 'Error',
        description: 'Please select at least one entity',
        variant: 'destructive'
      });
      return;
    }

    if (!selectedUser) {
      toast({
        title: 'Error',
        description: 'Please select a user',
        variant: 'destructive'
      });
      return;
    }

    setLoading(true);
    setProgress(0);
    setResults(null);

    try {
      // Prepare assignments
      const assignments = selectedEntities.map(entityId => {
        const entity = entities.find(e => e.id === entityId);
        return {
          entity_type: entity?.type || 'task',
          entity_id: entityId,
          user_id: selectedUser,
          assignment_type: assignmentType
        };
      });

      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const response = await api.post('/assignments/bulk', assignments);
      
      clearInterval(progressInterval);
      setProgress(100);
      
      const bulkResults: BulkAssignmentResult = response.data;
      setResults(bulkResults);

      if (bulkResults.successful.length > 0) {
        toast({
          title: 'Bulk Assignment Complete',
          description: `Successfully assigned ${bulkResults.successful.length} of ${bulkResults.total} entities`
        });
      }

      if (bulkResults.failed.length > 0) {
        toast({
          title: 'Some Assignments Failed',
          description: `${bulkResults.failed.length} assignments failed. Check the results below.`,
          variant: 'destructive'
        });
      }

      onAssignmentComplete?.(bulkResults);
      
      // Reset form
      setSelectedEntities([]);
      setSelectedUser('');
      
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to perform bulk assignment',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
      setTimeout(() => setProgress(0), 2000);
    }
  };

  const getEntityTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      'task': 'bg-blue-100 text-blue-800',
      'subtask': 'bg-green-100 text-green-800',
      'userstory': 'bg-purple-100 text-purple-800',
      'usecase': 'bg-orange-100 text-orange-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  const getAssignmentTypeOptions = () => {
    // Determine available assignment types based on selected entities
    const entityTypes = selectedEntities.map(id => 
      entities.find(e => e.id === id)?.type
    ).filter(Boolean);

    const uniqueTypes = [...new Set(entityTypes)];
    
    if (uniqueTypes.every(type => ['task', 'subtask'].includes(type!))) {
      return [{ value: 'developer', label: 'Developer' }];
    }
    
    if (uniqueTypes.every(type => ['usecase', 'userstory', 'project', 'program'].includes(type!))) {
      return [{ value: 'owner', label: 'Owner' }];
    }
    
    if (uniqueTypes.every(type => type === 'client')) {
      return [{ value: 'contact_person', label: 'Contact Person' }];
    }

    // Mixed types - show all options
    return [
      { value: 'owner', label: 'Owner' },
      { value: 'developer', label: 'Developer' },
      { value: 'contact_person', label: 'Contact Person' }
    ];
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Upload className="w-5 h-5 mr-2" />
          Bulk Assignment
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Entity Selection */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <Label>Select Entities ({selectedEntities.length} of {entities.length})</Label>
            <Button
              variant="outline"
              size="sm"
              onClick={handleSelectAll}
            >
              {selectedEntities.length === entities.length ? 'Deselect All' : 'Select All'}
            </Button>
          </div>
          
          <div className="max-h-48 overflow-y-auto border rounded-lg p-2 space-y-2">
            {entities.map((entity) => (
              <div
                key={entity.id}
                className="flex items-center space-x-3 p-2 hover:bg-muted/50 rounded"
              >
                <Checkbox
                  checked={selectedEntities.includes(entity.id)}
                  onCheckedChange={() => handleEntityToggle(entity.id)}
                />
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium text-sm">{entity.name}</span>
                    <Badge className={getEntityTypeColor(entity.type)}>
                      {entity.type}
                    </Badge>
                  </div>
                  {entity.current_assignment && (
                    <div className="text-xs text-muted-foreground">
                      Current: {entity.current_assignment}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Assignment Configuration */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label>Assignment Type</Label>
            <Select value={assignmentType} onValueChange={setAssignmentType}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {getAssignmentTypeOptions().map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>Assign To User</Label>
            <Select value={selectedUser} onValueChange={setSelectedUser}>
              <SelectTrigger>
                <SelectValue placeholder="Select user" />
              </SelectTrigger>
              <SelectContent>
                {users.map((user) => (
                  <SelectItem key={user.id} value={user.id}>
                    <div className="flex items-center">
                      <Users className="w-4 h-4 mr-2" />
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
        </div>

        {/* Progress */}
        {loading && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Processing assignments...</span>
              <span>{progress}%</span>
            </div>
            <Progress value={progress} />
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="space-y-3">
            <Label>Assignment Results</Label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center space-x-2 p-3 border rounded-lg">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <div>
                  <div className="font-medium text-green-600">Successful</div>
                  <div className="text-sm text-muted-foreground">{results.successful.length}</div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2 p-3 border rounded-lg">
                <XCircle className="w-5 h-5 text-red-600" />
                <div>
                  <div className="font-medium text-red-600">Failed</div>
                  <div className="text-sm text-muted-foreground">{results.failed.length}</div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2 p-3 border rounded-lg">
                <AlertCircle className="w-5 h-5 text-blue-600" />
                <div>
                  <div className="font-medium text-blue-600">Total</div>
                  <div className="text-sm text-muted-foreground">{results.total}</div>
                </div>
              </div>
            </div>

            {results.failed.length > 0 && (
              <div className="space-y-2">
                <Label className="text-red-600">Failed Assignments</Label>
                <div className="max-h-32 overflow-y-auto border rounded-lg p-2 space-y-1">
                  {results.failed.map((failure, index) => (
                    <div key={index} className="text-sm p-2 bg-red-50 rounded">
                      <div className="font-medium">{failure.entity_type}:{failure.entity_id}</div>
                      <div className="text-red-600">{failure.error}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end">
          <Button
            onClick={handleBulkAssign}
            disabled={loading || selectedEntities.length === 0 || !selectedUser}
          >
            {loading ? 'Assigning...' : `Assign ${selectedEntities.length} Entities`}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
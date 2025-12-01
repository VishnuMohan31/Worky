/**
 * Manual API Verification Script for Subtasks
 * 
 * This script can be used to manually verify the subtask API integration
 * by making real API calls to the backend.
 * 
 * To run this script:
 * 1. Ensure the API server is running
 * 2. Update the AUTH_TOKEN with a valid token
 * 3. Run: npx tsx ui/src/services/__tests__/verify-subtask-api.ts
 * 
 * Requirements: 4.11, 4.12
 */

import api from '../api';

// Configuration
const AUTH_TOKEN = 'your-auth-token-here'; // Replace with actual token
const TEST_TASK_ID = 'task-id-here'; // Replace with actual task ID

// Store token for API calls
if (typeof localStorage !== 'undefined') {
  localStorage.setItem('token', AUTH_TOKEN);
}

interface TestResult {
  test: string;
  status: 'PASS' | 'FAIL' | 'SKIP';
  message: string;
  error?: any;
}

const results: TestResult[] = [];

async function runTests() {
  console.log('🚀 Starting Subtask API Verification Tests\n');
  console.log('=' .repeat(60));
  
  // Test 1: Get Subtasks
  try {
    console.log('\n📋 Test 1: GET /subtasks (all subtasks)');
    const subtasks = await api.getSubtasks();
    
    if (Array.isArray(subtasks)) {
      results.push({
        test: 'api.getSubtasks()',
        status: 'PASS',
        message: `Retrieved ${subtasks.length} subtasks`
      });
      console.log(`✅ PASS: Retrieved ${subtasks.length} subtasks`);
      
      if (subtasks.length > 0) {
        console.log('   Sample subtask:', JSON.stringify(subtasks[0], null, 2));
      }
    } else {
      results.push({
        test: 'api.getSubtasks()',
        status: 'FAIL',
        message: 'Response is not an array'
      });
      console.log('❌ FAIL: Response is not an array');
    }
  } catch (error: any) {
    results.push({
      test: 'api.getSubtasks()',
      status: 'FAIL',
      message: error.message || 'Unknown error',
      error
    });
    console.log('❌ FAIL:', error.message);
    console.log('   Error details:', error.response?.data || error);
  }
  
  // Test 2: Get Subtasks by Task ID
  if (TEST_TASK_ID !== 'task-id-here') {
    try {
      console.log(`\n📋 Test 2: GET /subtasks?task_id=${TEST_TASK_ID}`);
      const taskSubtasks = await api.getSubtasks(TEST_TASK_ID);
      
      if (Array.isArray(taskSubtasks)) {
        results.push({
          test: 'api.getSubtasks(taskId)',
          status: 'PASS',
          message: `Retrieved ${taskSubtasks.length} subtasks for task ${TEST_TASK_ID}`
        });
        console.log(`✅ PASS: Retrieved ${taskSubtasks.length} subtasks for task`);
      } else {
        results.push({
          test: 'api.getSubtasks(taskId)',
          status: 'FAIL',
          message: 'Response is not an array'
        });
        console.log('❌ FAIL: Response is not an array');
      }
    } catch (error: any) {
      results.push({
        test: 'api.getSubtasks(taskId)',
        status: 'FAIL',
        message: error.message || 'Unknown error',
        error
      });
      console.log('❌ FAIL:', error.message);
    }
  } else {
    results.push({
      test: 'api.getSubtasks(taskId)',
      status: 'SKIP',
      message: 'TEST_TASK_ID not configured'
    });
    console.log('\n⏭️  Test 2: SKIPPED (TEST_TASK_ID not configured)');
  }
  
  // Test 3: Create Subtask
  if (TEST_TASK_ID !== 'task-id-here') {
    try {
      console.log('\n📋 Test 3: POST /subtasks/ (create subtask)');
      const newSubtask = await api.createEntity('subtask', {
        task_id: TEST_TASK_ID,
        title: 'Test Subtask - API Verification',
        status: 'To Do',
        estimated_hours: 2,
        duration_days: 1,
        short_description: 'This is a test subtask created by the verification script'
      });
      
      if (newSubtask && newSubtask.id) {
        results.push({
          test: 'api.createEntity("subtask", data)',
          status: 'PASS',
          message: `Created subtask with ID: ${newSubtask.id}`
        });
        console.log(`✅ PASS: Created subtask with ID: ${newSubtask.id}`);
        console.log('   Created subtask:', JSON.stringify(newSubtask, null, 2));
        
        // Test 4: Update Subtask
        try {
          console.log(`\n📋 Test 4: PUT /subtasks/${newSubtask.id} (update subtask)`);
          const updatedSubtask = await api.updateEntity('subtask', newSubtask.id, {
            status: 'In Progress',
            estimated_hours: 3
          });
          
          if (updatedSubtask && updatedSubtask.status === 'In Progress') {
            results.push({
              test: 'api.updateEntity("subtask", id, data)',
              status: 'PASS',
              message: `Updated subtask ${newSubtask.id} successfully`
            });
            console.log(`✅ PASS: Updated subtask successfully`);
            console.log('   Updated subtask:', JSON.stringify(updatedSubtask, null, 2));
          } else {
            results.push({
              test: 'api.updateEntity("subtask", id, data)',
              status: 'FAIL',
              message: 'Update did not reflect expected changes'
            });
            console.log('❌ FAIL: Update did not reflect expected changes');
          }
        } catch (error: any) {
          results.push({
            test: 'api.updateEntity("subtask", id, data)',
            status: 'FAIL',
            message: error.message || 'Unknown error',
            error
          });
          console.log('❌ FAIL:', error.message);
          console.log('   Error details:', error.response?.data || error);
        }
        
        // Test 5: Delete Subtask (cleanup)
        try {
          console.log(`\n📋 Test 5: DELETE /subtasks/${newSubtask.id} (cleanup)`);
          await api.deleteEntity('subtask', newSubtask.id);
          console.log(`✅ Cleanup: Deleted test subtask ${newSubtask.id}`);
        } catch (error: any) {
          console.log(`⚠️  Warning: Could not delete test subtask: ${error.message}`);
        }
        
      } else {
        results.push({
          test: 'api.createEntity("subtask", data)',
          status: 'FAIL',
          message: 'Created subtask missing ID'
        });
        console.log('❌ FAIL: Created subtask missing ID');
      }
    } catch (error: any) {
      results.push({
        test: 'api.createEntity("subtask", data)',
        status: 'FAIL',
        message: error.message || 'Unknown error',
        error
      });
      console.log('❌ FAIL:', error.message);
      console.log('   Error details:', error.response?.data || error);
      
      // Skip update test if create failed
      results.push({
        test: 'api.updateEntity("subtask", id, data)',
        status: 'SKIP',
        message: 'Skipped due to create failure'
      });
    }
  } else {
    results.push({
      test: 'api.createEntity("subtask", data)',
      status: 'SKIP',
      message: 'TEST_TASK_ID not configured'
    });
    results.push({
      test: 'api.updateEntity("subtask", id, data)',
      status: 'SKIP',
      message: 'TEST_TASK_ID not configured'
    });
    console.log('\n⏭️  Test 3 & 4: SKIPPED (TEST_TASK_ID not configured)');
  }
  
  // Test 6: Error Handling - 404
  try {
    console.log('\n📋 Test 6: Error Handling - 404 Not Found');
    await api.updateEntity('subtask', 'non-existent-id', { status: 'Done' });
    results.push({
      test: 'Error Handling - 404',
      status: 'FAIL',
      message: 'Expected 404 error but request succeeded'
    });
    console.log('❌ FAIL: Expected 404 error but request succeeded');
  } catch (error: any) {
    if (error.response?.status === 404) {
      results.push({
        test: 'Error Handling - 404',
        status: 'PASS',
        message: '404 error correctly thrown and caught'
      });
      console.log('✅ PASS: 404 error correctly thrown and caught');
      console.log('   Error message:', error.response?.data?.detail);
    } else {
      results.push({
        test: 'Error Handling - 404',
        status: 'FAIL',
        message: `Expected 404 but got ${error.response?.status || 'unknown error'}`
      });
      console.log(`❌ FAIL: Expected 404 but got ${error.response?.status || 'unknown error'}`);
    }
  }
  
  // Test 7: Error Handling - Validation Error
  if (TEST_TASK_ID !== 'task-id-here') {
    try {
      console.log('\n📋 Test 7: Error Handling - 400 Validation Error');
      await api.createEntity('subtask', {
        task_id: TEST_TASK_ID,
        title: '', // Invalid: empty title
        estimated_hours: -1, // Invalid: negative hours
        duration_days: 0 // Invalid: zero days
      });
      results.push({
        test: 'Error Handling - 400',
        status: 'FAIL',
        message: 'Expected 400 validation error but request succeeded'
      });
      console.log('❌ FAIL: Expected 400 validation error but request succeeded');
    } catch (error: any) {
      if (error.response?.status === 400 || error.response?.status === 422) {
        results.push({
          test: 'Error Handling - 400',
          status: 'PASS',
          message: 'Validation error correctly thrown and caught'
        });
        console.log('✅ PASS: Validation error correctly thrown and caught');
        console.log('   Error details:', error.response?.data?.detail);
      } else {
        results.push({
          test: 'Error Handling - 400',
          status: 'FAIL',
          message: `Expected 400/422 but got ${error.response?.status || 'unknown error'}`
        });
        console.log(`❌ FAIL: Expected 400/422 but got ${error.response?.status || 'unknown error'}`);
      }
    }
  } else {
    results.push({
      test: 'Error Handling - 400',
      status: 'SKIP',
      message: 'TEST_TASK_ID not configured'
    });
    console.log('\n⏭️  Test 7: SKIPPED (TEST_TASK_ID not configured)');
  }
  
  // Print Summary
  console.log('\n' + '='.repeat(60));
  console.log('📊 TEST SUMMARY');
  console.log('='.repeat(60));
  
  const passed = results.filter(r => r.status === 'PASS').length;
  const failed = results.filter(r => r.status === 'FAIL').length;
  const skipped = results.filter(r => r.status === 'SKIP').length;
  
  console.log(`\n✅ Passed: ${passed}`);
  console.log(`❌ Failed: ${failed}`);
  console.log(`⏭️  Skipped: ${skipped}`);
  console.log(`📝 Total: ${results.length}`);
  
  console.log('\n📋 Detailed Results:');
  results.forEach((result, index) => {
    const icon = result.status === 'PASS' ? '✅' : result.status === 'FAIL' ? '❌' : '⏭️';
    console.log(`${index + 1}. ${icon} ${result.test}: ${result.message}`);
  });
  
  console.log('\n' + '='.repeat(60));
  
  if (failed === 0 && passed > 0) {
    console.log('🎉 All tests passed! API integration is working correctly.');
  } else if (skipped === results.length) {
    console.log('⚠️  All tests skipped. Please configure AUTH_TOKEN and TEST_TASK_ID.');
  } else if (failed > 0) {
    console.log('⚠️  Some tests failed. Please review the errors above.');
  }
  
  console.log('='.repeat(60) + '\n');
}

// Run tests if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  runTests().catch(console.error);
}

export { runTests };

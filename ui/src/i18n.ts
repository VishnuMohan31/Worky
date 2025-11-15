import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

const resources = {
  en: {
    translation: {
      // Navigation
      dashboard: 'Dashboard',
      clients: 'Clients',
      programs: 'Programs',
      projects: 'Projects',
      useCases: 'Use Cases',
      userStories: 'User Stories',
      tasks: 'Tasks',
      subtasks: 'Subtasks',
      gantt: 'Gantt Chart',
      kanban: 'Kanban Board',
      sprint: 'Sprint Board',
      bugs: 'Bugs',
      reports: 'Reports',
      users: 'Users',
      profile: 'Profile',
      logout: 'Logout',
      phases: 'Phases',
      hierarchy: 'Hierarchy',
      
      // Common
      save: 'Save',
      cancel: 'Cancel',
      delete: 'Delete',
      edit: 'Edit',
      create: 'Create',
      search: 'Search',
      filter: 'Filter',
      export: 'Export',
      loading: 'Loading...',
      noData: 'No data available',
      add: 'Add',
      view: 'View',
      update: 'Update',
      close: 'Close',
      confirm: 'Confirm',
      back: 'Back',
      next: 'Next',
      
      // Hierarchy Navigation
      parent: 'Parent',
      children: 'Children',
      breadcrumb: 'Breadcrumb',
      navigateUp: 'Navigate Up',
      navigateDown: 'Navigate Down',
      viewDetails: 'View Details',
      addChild: 'Add Child',
      
      // Entity Types
      client: 'Client',
      program: 'Program',
      project: 'Project',
      useCase: 'Use Case',
      userStory: 'User Story',
      task: 'Task',
      subtask: 'Subtask',
      bug: 'Bug',
      phase: 'Phase',
      
      // Statistics
      statistics: 'Statistics',
      statusDistribution: 'Status Distribution',
      phaseDistribution: 'Phase Distribution',
      completionPercentage: 'Completion Percentage',
      rollupCounts: 'Rollup Counts',
      totalCount: 'Total Count',
      
      // Status
      notStarted: 'Not Started',
      inProgress: 'In Progress',
      completed: 'Completed',
      blocked: 'Blocked',
      toDo: 'To Do',
      inReview: 'In Review',
      done: 'Done',
      
      // Phases
      development: 'Development',
      analysis: 'Analysis',
      design: 'Design',
      testing: 'Testing',
      
      // Bug Management
      severity: 'Severity',
      priority: 'Priority',
      assignedTo: 'Assigned To',
      reportedBy: 'Reported By',
      resolutionNotes: 'Resolution Notes',
      assignBug: 'Assign Bug',
      resolveBug: 'Resolve Bug',
      
      // Audit
      auditHistory: 'Audit History',
      action: 'Action',
      changedBy: 'Changed By',
      changedAt: 'Changed At',
      changes: 'Changes',
      oldValue: 'Old Value',
      newValue: 'New Value',
      
      // Auth
      login: 'Login',
      email: 'Email',
      password: 'Password',
      welcomeBack: 'Welcome Back',
      loginToContinue: 'Login to continue to Worky',
      
      // Theme
      theme: 'Theme',
      snow: 'Snow',
      greenery: 'Greenery',
      water: 'Water',
      dracula: 'Dracula',
      dark: 'Dark',
      blackwhite: 'Black & White',
      
      // Language
      language: 'Language',
      english: 'English',
      telugu: 'Telugu'
    }
  },
  te: {
    translation: {
      // Navigation
      dashboard: 'డాష్‌బోర్డ్',
      clients: 'క్లయింట్లు',
      programs: 'ప్రోగ్రామ్‌లు',
      projects: 'ప్రాజెక్ట్‌లు',
      useCases: 'వినియోగ కేసులు',
      userStories: 'వినియోగదారు కథలు',
      tasks: 'టాస్క్‌లు',
      subtasks: 'ఉప టాస్క్‌లు',
      gantt: 'గాంట్ చార్ట్',
      kanban: 'కాన్బాన్ బోర్డ్',
      sprint: 'స్ప్రింట్ బోర్డ్',
      bugs: 'బగ్‌లు',
      reports: 'రిపోర్ట్‌లు',
      users: 'వినియోగదారులు',
      profile: 'ప్రొఫైల్',
      logout: 'లాగ్అవుట్',
      phases: 'దశలు',
      hierarchy: 'క్రమానుగత',
      
      // Common
      save: 'సేవ్ చేయండి',
      cancel: 'రద్దు చేయండి',
      delete: 'తొలగించండి',
      edit: 'సవరించండి',
      create: 'సృష్టించండి',
      search: 'వెతకండి',
      filter: 'ఫిల్టర్',
      export: 'ఎగుమతి',
      loading: 'లోడ్ అవుతోంది...',
      noData: 'డేటా అందుబాటులో లేదు',
      add: 'జోడించండి',
      view: 'చూడండి',
      update: 'నవీకరించండి',
      close: 'మూసివేయండి',
      confirm: 'నిర్ధారించండి',
      back: 'వెనుకకు',
      next: 'తదుపరి',
      
      // Hierarchy Navigation
      parent: 'మాతృ',
      children: 'పిల్లలు',
      breadcrumb: 'బ్రెడ్‌క్రంబ్',
      navigateUp: 'పైకి నావిగేట్ చేయండి',
      navigateDown: 'క్రిందికి నావిగేట్ చేయండి',
      viewDetails: 'వివరాలు చూడండి',
      addChild: 'పిల్లను జోడించండి',
      
      // Entity Types
      client: 'క్లయింట్',
      program: 'ప్రోగ్రామ్',
      project: 'ప్రాజెక్ట్',
      useCase: 'వినియోగ కేసు',
      userStory: 'వినియోగదారు కథ',
      task: 'టాస్క్',
      subtask: 'ఉప టాస్క్',
      bug: 'బగ్',
      phase: 'దశ',
      
      // Statistics
      statistics: 'గణాంకాలు',
      statusDistribution: 'స్థితి పంపిణీ',
      phaseDistribution: 'దశ పంపిణీ',
      completionPercentage: 'పూర్తి శాతం',
      rollupCounts: 'రోల్అప్ గణనలు',
      totalCount: 'మొత్తం గణన',
      
      // Status
      notStarted: 'ప్రారంభించలేదు',
      inProgress: 'పురోగతిలో ఉంది',
      completed: 'పూర్తయింది',
      blocked: 'నిరోధించబడింది',
      toDo: 'చేయవలసినది',
      inReview: 'సమీక్షలో',
      done: 'పూర్తయింది',
      
      // Phases
      development: 'అభివృద్ధి',
      analysis: 'విశ్లేషణ',
      design: 'రూపకల్పన',
      testing: 'పరీక్ష',
      
      // Bug Management
      severity: 'తీవ్రత',
      priority: 'ప్రాధాన్యత',
      assignedTo: 'కేటాయించబడింది',
      reportedBy: 'నివేదించినవారు',
      resolutionNotes: 'పరిష్కార గమనికలు',
      assignBug: 'బగ్‌ను కేటాయించండి',
      resolveBug: 'బగ్‌ను పరిష్కరించండి',
      
      // Audit
      auditHistory: 'ఆడిట్ చరిత్ర',
      action: 'చర్య',
      changedBy: 'మార్చినవారు',
      changedAt: 'మార్చిన సమయం',
      changes: 'మార్పులు',
      oldValue: 'పాత విలువ',
      newValue: 'కొత్త విలువ',
      
      // Auth
      login: 'లాగిన్',
      email: 'ఇమెయిల్',
      password: 'పాస్‌వర్డ్',
      welcomeBack: 'తిరిగి స్వాగతం',
      loginToContinue: 'Worky కొనసాగించడానికి లాగిన్ చేయండి',
      
      // Theme
      theme: 'థీమ్',
      snow: 'మంచు',
      greenery: 'పచ్చదనం',
      water: 'నీరు',
      dracula: 'డ్రాక్యులా',
      dark: 'చీకటి',
      blackwhite: 'నలుపు & తెలుపు',
      
      // Language
      language: 'భాష',
      english: 'ఇంగ్లీష్',
      telugu: 'తెలుగు'
    }
  }
}

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: localStorage.getItem('language') || 'en',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  })

export default i18n

const projectMeta = {
  projectName: 'NL2UML',
  version: 'v0.1.0',
  abstract: 'NL2UML transforms natural-language software requirements into editable UML diagrams using an LLM-powered pipeline backed by PlantUML rendering and export tools. Sessions stay isolated via random identifiers so research feedback and diagram iterations can be traced to a single workspace.',
  technologies: [
    'React + React Router + Bootstrap UI',
    'Flask API orchestrating Ollama-hosted LLMs',
    'PlantUML generation, PNG/PDF exports, and session storage',
    'Dockerized stack with SQLite persistence'
  ],
  documentation: {
    primary: {
      label: 'Project README',
      url: 'https://github.com/NateShaq/uco-grad-capstone-nl2uml/blob/main/README.md'
    },
    report: {
      label: 'Capstone overview',
      url: 'https://github.com/NateShaq/uco-grad-capstone-nl2uml'
    }
  },
  university: {
    name: 'University of Central Oklahoma',
    location: 'Edmond, Oklahoma',
    description: 'The University of Central Oklahoma (UCO) is a metropolitan public university located in Edmond, Oklahoma, and one of the state’s oldest institutions of higher education. UCO is nationally recognized for its commitment to transformative learning, hands-on research, and preparing future leaders through high-impact academic programs across science, engineering, business, and the arts.'
  },
  department: {
    name: 'Department of Computer Science',
    description: 'The Department of Computer Science at the University of Central Oklahoma provides ABET-accredited programs with a strong emphasis on software engineering, artificial intelligence, cybersecurity, systems architecture, and cloud computing. The department blends rigorous academic foundations with hands-on applied research, preparing graduates for modern industry challenges and leadership roles in technology.'
  },
  professor: {
    name: 'Dr. Jicheng Fu, Ph.D.',
    title: 'John T. Beresford Endowed Chair, Department of Computer Science, University of Central Oklahoma',
    interests: [
      'Artificial Intelligence',
      'Software Engineering',
      'Cloud/Mobile Computing'
    ],
    link: 'https://www3.uco.edu/centraldirectory/profiles/765592'
  },
  student: {
    name: 'Nathaniel Brock',
    link: 'https://www.linkedin.com/in/nathaniel-brock-a9925723/'
  }
};

export default projectMeta;

const projectMeta = {
  projectName: 'NL2UML',
  version: 'v0.1.0',
  abstract: 'NL2UML is an LLM-driven platform that turns natural-language software requirements into structured, editable UML diagrams. It orchestrates a multi-stage pipeline—model selection, prompt templating, and PlantUML rendering—to produce accurate diagrams while balancing latency, compute, and resource constraints within finite context windows. Each session is isolated via randomized identifiers, enabling reproducible experimentation and iterative refinement as specifications evolve. By surfacing a global view of infrastructure, class structure, and design patterns, the system keeps the codebase aligned with both initial intent and ongoing changes. As a research prototype, NL2UML demonstrates how agent-assisted workflows bridge textual specification and visual modeling, preserving coherence from early design through implementation.',
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

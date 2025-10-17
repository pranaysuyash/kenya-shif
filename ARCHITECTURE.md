# System Architecture and Workflow

This document provides an overview of the system architecture and data flow for the Kenya SHIF Healthcare Policy Analyzer.

## High-Level Architecture

The application is designed with a three-tiered architecture:

1.  **Presentation Layer (UI)**: The user interface is a web-based dashboard built with Streamlit.
2.  **Application Logic/Service Layer**: This layer contains the core analysis engines, which are responsible for processing the data and generating insights.
3.  **Data Layer**: This layer consists of the source PDF document, the file system for storing outputs and cache, and the OpenAI API for AI-powered analysis.

### Architecture Diagram

The following diagram illustrates the high-level architecture of the system:

```mermaid
graph TD
    subgraph "Presentation Layer"
        A[Streamlit UI]
    end

    subgraph "Application Logic/Service Layer"
        B[Analysis Engine]
    end

    subgraph "Data Layer"
        C[PDF Document (SHI Tariffs)]
        D[File System (Outputs & Cache)]
        E[OpenAI API]
    end

    A --> B

    subgraph "Analysis Engine"
        B1[Integrated Comprehensive Analyzer]
        B2[SHIF Healthcare Pattern Analyzer]
    end

    B1 --> C
    B1 --> D
    B1 --> E

    B2 --> B1
    B2 --> D
```

**Components:**

*   **Streamlit UI (`streamlit_comprehensive_analyzer.py`)**: The entry point for the user. It provides controls to run analyses and displays the results in an interactive dashboard.
*   **Analysis Engine**:
    *   **Integrated Comprehensive Analyzer (`integrated_comprehensive_analyzer.py`)**: The primary analysis engine. It combines rule-based data extraction with AI-powered analysis using the OpenAI API to identify contradictions, gaps, and other insights.
    *   **SHIF Healthcare Pattern Analyzer (`shif_healthcare_pattern_analyzer.py`)**: A pattern-based analyzer that can also leverage the integrated analyzer for data extraction. It uses regular expressions and pattern matching to analyze the data.
*   **Data Layer**:
    *   **PDF Document (`TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf`)**: The source document containing the healthcare policy information.
    *   **File System**: Used to store the outputs of the analysis (in `outputs_run_*` and `outputs_pattern_*` directories) and to cache AI responses (in the `ai_cache` directory).
    *   **OpenAI API**: Used by the `Integrated Comprehensive Analyzer` to perform advanced AI-powered analysis.

## Application Workflow

The following diagram illustrates the main user workflows and data flow through the application:

### Flow Diagram

```mermaid
graph TD
    A[User in Streamlit UI] --> B{Choose Action}

    B --> C[Run Pattern Analysis]
    B --> D[Run Integrated Analysis]
    B --> E[Load Existing Results]

    C --> C1[SHIF Healthcare Pattern Analyzer]
    C1 --> C2[Loads Verified Dataset from Integrated Analyzer]
    C2 --> C3[Task 1: Structure Rules]
    C3 --> C4[Task 2: Detect Contradictions & Gaps]
    C4 --> C5[Task 3: Integrate Kenya Context]
    C5 --> C6[Task 4: Create Dashboard]
    C6 --> F[Displayed in Streamlit UI]

    D --> D1[Integrated Comprehensive Analyzer]
    D1 --> D2[Phase 1: Build Vocabulary]
    D2 --> D3[Phase 2 & 3: Extract Data from PDF]
    D3 --> D4[Phase 4: AI-Enhanced Analysis (OpenAI API)]
    D4 --> D5[Phase 5: Integrate Results]
    D5 --> F

    E --> E1[Load Analysis from File System]
    E1 --> F
```

**Workflow Steps:**

1.  **User Interaction**: The user interacts with the application through the Streamlit UI.
2.  **Action Selection**: The user can choose to:
    *   **Run Pattern Analysis**: This triggers the `SHIFHealthcarePatternAnalyzer`, which uses the `IntegratedComprehensiveAnalyzer` to extract the data and then applies its own pattern-based analysis.
    *   **Run Integrated Analysis**: This triggers the `IntegratedComprehensiveAnalyzer`, which performs a full data extraction and AI-powered analysis pipeline.
    *   **Load Existing Results**: This loads previously generated analysis results from the file system.
3.  **Analysis Execution**:
    *   The selected analyzer processes the PDF document, extracts the data, and performs the analysis (either pattern-based or AI-based).
    *   The results are saved to the file system in a timestamped directory.
4.  **Display Results**: The results of the analysis are then passed back to the Streamlit UI, where they are displayed to the user in the form of tables, charts, and downloadable reports.

# Backend

The backend will handle the core recommendation logic of the Ayurveda
formulation recommendation system.

## Main Responsibilities

- Receive disease or symptom information from the frontend.
- Normalize disease names and handle known synonyms.
- Search the Ayurveda formulation dataset.
- Match diseases with suitable formulations.
- Check formulation ingredients and Ayurvedic properties.
- Filter unsuitable formulations.
- Return ranked recommendations to the frontend.

## Basic Processing Flow

User Input
    ↓
Disease / Symptom Identification
    ↓
Disease Normalization
    ↓
Formulation Search
    ↓
Ingredient & Property Matching
    ↓
Filtering
    ↓
Recommendation
    ↓
Frontend

## Planned Components

### Recommendation Engine
Responsible for matching the user's condition with suitable
Ayurvedic formulations.

### Disease Mapper
Handles alternative names and synonyms for diseases.

### Formulation Matcher
Checks the relationship between diseases, formulations and ingredients.

### Property Checker
Provides Ayurvedic properties such as:

- Rasa
- Guna
- Virya
- Vipaka

### Recommendation Response
Returns the selected formulations along with their relevant information
and references.

## Current Status

Basic project structure and data model are being developed.
The recommendation engine will be implemented incrementally.

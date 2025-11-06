# Collaboration Workflow

This document outlines how Designer and Engineer collaborate asynchronously through this GitHub repository.

## The Pattern

**Designer (Claude Desktop)** and **Engineer (Claude Code)** communicate by:
1. Creating/updating markdown documents in `/docs`
2. Committing code changes to their respective directories
3. Using GitHub as the message bus for coordination

## Communication Channels

### Designer → Engineer
- Creates specification documents in `/docs`
- Opens issues for implementation tasks
- Reviews completed work and provides feedback

### Engineer → Designer  
- Creates `AUDIT-RESULTS.md` with system information
- Implements specs and commits code
- Asks clarifying questions via documents or comments

### Both Directions
- Update README.md status checklist as work progresses
- Use clear commit messages describing changes
- Reference related documents in commits

## Document Conventions

### Request Documents
Format: `[TOPIC]-REQUEST.md`
- Clear questions or requirements
- Checkboxes for items to complete
- Examples of expected format
- Timeline/urgency if applicable

### Response Documents  
Format: `[TOPIC]-RESULTS.md` or `[TOPIC]-RESPONSE.md`
- Answers to all questions
- Data in requested format
- Recommendations or concerns
- Links to related code/commits

### Specification Documents
Format: `[COMPONENT]-SPEC.md`
- Complete technical specifications
- Architecture decisions
- Implementation requirements
- Success criteria
- Testing approach

## Code Organization

### `/penpot-plugin`
- Engineer implements PenPot plugin based on Designer's specs
- TypeScript/JavaScript code
- Follows PenPot plugin conventions

### `/mcp-server`
- Engineer implements MCP server based on Designer's specs  
- Python or Node.js (as determined by audit)
- RESTful API design

### `/mcp-configs`
- Both agents contribute their respective configs
- JSON format
- Documented with comments

## Workflow Example

1. **Designer** creates `AUDIT-REQUEST.md`
2. **Sean** tells Engineer to check the repo
3. **Engineer** responds with `AUDIT-RESULTS.md`
4. **Designer** reads results, creates `PLUGIN-SPEC.md` and `MCP-SERVER-SPEC.md`
5. **Engineer** implements according to specs, commits code
6. **Designer** reviews code, provides feedback or approval
7. **Both** iterate until complete

## Status Updates

Update the checklist in README.md after completing each phase:
```markdown
- [x] Repository created
- [x] Basic structure defined
- [x] System audit completed  ← Update this after AUDIT-RESULTS.md
- [ ] Architecture finalized
- [ ] PenPot plugin developed
```

## Questions and Clarifications

If either agent needs clarification:
1. Create a new document: `QUESTION-[topic].md`
2. Reference the related spec/document
3. Wait for response document

## Best Practices

- **Be specific**: Include exact commands, file paths, code examples
- **Be complete**: Don't assume context, state everything clearly
- **Be async-friendly**: Provide all info needed to work independently
- **Be documented**: Explain *why* decisions were made, not just *what*

## Human (Sean) in the Loop

Sean will:
- Relay messages between agents when needed
- Make final decisions on architectural choices
- Test completed implementations
- Approve before moving to next phase

Sean should NOT need to:
- Translate technical details between agents
- Fill in missing information from incomplete specs
- Guess at requirements or intentions

"""
Test script for the Agent and Team classes.
"""
import asyncio
from agentic_framework.core.agent import Agent, AgentConfig, AgentType, AutonomousAgent
from agentic_framework.core.team import Team, TeamRole


async def test_autonomous_agent():
    """Test basic autonomous agent functionality."""
    print("\n=== Testing Autonomous Agent ===")
    
    # Create agent configuration
    config = AgentConfig(
        name="test_agent",
        agent_type=AgentType.AUTONOMOUS,
        description="A test autonomous agent",
        capabilities=["reasoning", "planning"],
        verbose=True
    )
    
    # Create and initialize the agent
    agent = AutonomousAgent(config)
    
    # Test basic properties
    print(f"Agent created: {agent}")
    print(f"Agent state: {agent.state}")
    print(f"Agent config: {agent.config}")
    
    # Test task execution
    print("\nTesting task execution...")
    try:
        result = await agent.run_task("test task", param1="value1")
        print(f"Task result: {result}")
        print(f"Agent state after task: {agent.state}")
        print(f"Agent memory size: {len(agent.memory)}")
    except Exception as e:
        print(f"Error during task execution: {e}")
    
    # Test observation
    print("\nTesting observation...")
    agent.observe({"event": "test_observation", "data": "sample data"})
    print(f"Agent memory after observation: {agent.memory}")
    
    # Test reflection
    reflection = agent.reflect()
    print(f"Agent reflection: {reflection}")
    
    return agent


async def test_team_operations():
    """Test team creation and operations."""
    print("\n=== Testing Team Operations ===")
    
    # Create a team
    team = Team("engineering")
    print(f"Team created: {team}")
    
    # Create and add agents to the team
    agents = []
    
    # Create a manager agent
    manager_config = AgentConfig(
        name="manager",
        agent_type=AgentType.AUTONOMOUS,
        description="Team manager"
    )
    manager = AutonomousAgent(manager_config)
    team.add_member(manager, roles=[TeamRole.LEADER], capabilities=["management", "decision_making"])
    agents.append(manager)
    
    # Create a developer agent
    dev_config = AgentConfig(
        name="developer",
        agent_type=AgentType.AUTONOMOUS,
        description="Software developer"
    )
    developer = AutonomousAgent(dev_config)
    team.add_member(developer, roles=[TeamRole.MEMBER], capabilities=["coding", "debugging"])
    agents.append(developer)
    
    # Create a tester agent
    tester_config = AgentConfig(
        name="tester",
        agent_type=AgentType.AUTONOMOUS,
        description="Quality assurance"
    )
    tester = AutonomousAgent(tester_config)
    team.add_member(tester, roles=[TeamRole.REVIEWER], capabilities=["testing", "qa"])
    agents.append(tester)
    
    # Print team status
    print("\nTeam members:")
    for agent in agents:
        status = team.get_member_status(agent.config.name)
        print(f"- {status['name']} (Roles: {', '.join(status['roles'])})")
    
    # Test task assignment
    print("\nTesting task assignment...")
    try:
        result = await team.assign_task("Implement feature X", assignee="developer")
        print(f"Task result: {result}")
    except Exception as e:
        print(f"Error during task assignment: {e}")
    
    # Test broadcasting a message
    print("\nTesting broadcast message...")
    await team.broadcast("Team meeting in 5 minutes!", sender="manager")
    
    # Print final agent states
    print("\nFinal agent states:")
    for agent in agents:
        print(f"- {agent.config.name}: {agent.state}")
    
    return team


async def main():
    """Run all tests."""
    print("=== Starting Agent Framework Tests ===")
    
    # Test autonomous agent
    agent = await test_autonomous_agent()
    
    # Test team operations
    team = await test_team_operations()
    
    print("\n=== All Tests Completed Successfully ===")


if __name__ == "__main__":
    asyncio.run(main())

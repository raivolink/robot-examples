# Example robot using Zendesk

This example contains a robot implementation that has the basic structure where one part consumes work items created from Zendesk and another part that consumes work items produced on previous step to update Zendesk ticket.

## Prerequisites

To run the example some preparation steps are needed.

### Zendesk

- Create webhook that will use Robocorp API to launch the process
- Create API access token(or any access that allows usage of API)
- For this example Zendesk macro was used to trigger webhook. Macro assigns tag to ticket and this triggers robot.

### Control Room

- Set up API key if none is created.
- Use API helper to configure endpoint _Start process with a single work item payload_
- Create process and add steps
- Create Vault entry, example uses ZendeskService as secret name.
- Create asset, example uses Zendesk-comment as asset name.

## Tasks

The robot is split into two tasks, meant to run as separate steps in Control Room. The first task consumes data sent from Zendesk and produces information for next step, and the second one reads and processes that data to update Zendesk ticket.

### The first task - Consume Zendesk Request

- Loads data from work item payload
- Generates message from data and creates output work item

This step can used for various actions, for example retriveing information from another systems, data man

### The second task - Send Zendesk Ticket Update

- Reads ticket id and message from work item
- Updates give ticket in Zendesk with message from work item

### Local testing

For best experience to test the work items in this example we recommend using [our VS Code extensions](https://robocorp.com/docs/developer-tools/visual-studio-code). With the Robocorp Code extension you can simply run and [select the input work items](https://robocorp.com/docs/developer-tools/visual-studio-code/extension-features#using-work-items) to use, create inputs to simulate error cases and so on.


# My Personal Portfolio Infrastructure

## Deploying this infrastructure

1. Change directory to the architecture of your choice.

2. Configure your infrastructure with the `config.yaml` file.

3. Synthesize the CloudFormation Templates:
    ```bash
    cdk synth
    ```

4. Deploy the GitHubConnection stack to connect your account to Github:
   ```bash
   cdk deploy GitHubConnection
   ```
    
5. Wait for the stack to finish deploying before continuing.

6. Accepting the GitHub connection 
   
   1. Go to [AWS CodeStar Connections](https://us-east-1.console.aws.amazon.com/codesuite/settings/connections).
   2. Choose the `github-portfolio-connection-sl` connection.
   3. Click `Update pending connection`.

7. Deploy the remaining stacks:
   ```bash
   cdk deploy --all --require-approval="never"
   ``` 

8. Once the stacks have deployed and the pipeline has finished building head over to your domain name. Keep in mind, if you have a fresh domain and hosted zone that your records can take over a day to propagate.

## Destroying this infrastructure

If you want to destroy the stacks simply run:
   ```bash
   cdk destroy --all --force
   ```

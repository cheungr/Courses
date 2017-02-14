Alexa Skill Kit Setup
===================


Hi! We'll have two things to set up. First, we'll need to set up the Alexa Skills Kit on [developers.amazon.com](https://developer.amazon.com/edw/home.html#/) and AWS Lambda on [aws.amazon.com](https://console.aws.amazon.com/lambda/home?region=us-east-1#/). 

----------


AWS Lambda
-------------

> **Note:**

> - Lambda functions for Alexa skills can be hosted in either the US East (N. Virginia) or EU (Ireland) region. These are the only regions the Alexa Skills Kit supports.


#### <i class="icon-file"></i> Create a ZIP

Zip up *index.js* along with the *node_modules* folder.

All your local documents are listed in the document panel. You can switch from one to another by clicking a document in the list or you can toggle documents using <kbd>Ctrl+[</kbd> and <kbd>Ctrl+]</kbd>.

#### <i class="icon-file"></i> Create Lambda Function

Make sure you're in the US East (N. Virginia) region.
![Click Create a Lambda Function](https://i.imgur.com/bSsy315.png)

Create a Blank Function
![Click the blank function blueprint](https://i.imgur.com/8rUuUTk.png)

Configure Alexa Skills Kit Trigger
![ASK Trigger](https://i.imgur.com/Eim60gt.png)
> **Tip:** The Alexa Skills Kit trigger is only avaliable in US East (N. Virginia) and EU (Ireland) regions. If you don't see it, you're in the wrong region.

Configure your function and upload the zipped up code you created. 
![Upload the code zip](https://i.imgur.com/rmUxKfE.png)

Select the default handler, and create a lambda_basic_execution role if you do not have an existing role. (leave everything default in the create a role process)
![function handler and role](https://i.imgur.com/piIkPEZ.png)

You're all done! You should see this:
![Success!](https://i.imgur.com/ZFthqi0.png)
> **Tip:**  Copy down the Lambda ARN (highlighted). You'll need this later on.


>**Tip:** Note the arrow pointing to var APP_ID. You'll need to update this with the APP ID that is created later on.



----------


Alexa Skill
-------------------

Alexa Skill is not part of aws, and is at [developers.amazon.com](https://developer.amazon.com/edw/home.html#/)

#### <i class="icon-file"></i> Create a Alexa Skills Kit Skill

Go to the amazon developers site > Alexa > Alexa Skills Kit
![Get Started ASK](https://i.imgur.com/dm6AhGe.png)

Enter the Name and Invocation Name as follows:
![Skill Info](https://i.imgur.com/P7fk7VP.png)
>**Tip:** Copy the Application ID and paste it into the var APP_ID in AWS Lambda code. You can edit this in-line in lambda.

Set up the Interaction Model.
![Interaction Model](https://i.imgur.com/X8BdQ32.png)
Copy IntentSchema.json into the Intent Schema section and SampleUtterences_en_US.txt into Sample Utterances section. These files in the SpeechAssets folder.

Configure the AWS Lambda Endpoint to Amazon Developer Alexa Skills Kit
![Paste the ARN you copied earlier into this field.](https://i.imgur.com/tKHwUWH.png)
Paste the ARN you copied earlier into this field. We are not using Account Linking as that requires oAuth. Click Next.

Enable Testing so you can test it on your Alexa device. (It needs to be on the same account for this to work. At the moment, there is no way to enable skills in development on other accounts)
![Enable Testing](https://i.imgur.com/ElgETW2.png)

EOF
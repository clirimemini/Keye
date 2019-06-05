## What is Keye?
Keye is a reconnaissance tool that was written in Python with SQLite3 integrated. After adding a list of URLs, it will make a request to these URLs and try to detect changes based on their response content length. This tool is supposed to be scheduled to run periodically at fixed times, dates, or intervals (Ideally each day). Recognized changes of URLs will be sent to Slack workspace with a notification push.

## Requirements
- Virtual Private Server (VPS) running on Unix.
- Python 2.x or 3.x.
- Free Slack workplace.

## Installation & Configuration
First of all, you will have to clone the tool from Github to your server:
> $ git clone https://github.com/clirimemini/Keye.git && cd Keye

Install the dependencies:

>$ python install -r requirements.txt (Or python3 install -r requirements.txt)

Next step is to create a Slack workspace, to where new recognized changes of URLs will be sent to. Just browse to [https://slack.com/](https://slack.com/) and create a free account.

Then, create a channel on your workspace.

Next, we need to generate a Webhook URL for our channel so we can leverage Slack API.

Browse to [https://api.slack.com/apps](https://api.slack.com/apps) and create a new application.

Browse to `Incoming Webhooks` and create a Webhook, and link it to the channel that we created previously.

You will obtain a link in the following format:

`https://hooks.slack.com/services/XXXXXXX/BF0XXXXME/XXXXXXXXXXXXX`

Copy that link and edit `slackconfig.py`

Now, we need to add a new Cron job to schedule execution of Keye at given time. To do it, type:
> $ crontab -e

Add the following line at the end of the Cron file:

`0 */12 * * * cd /root/Keye/ && /usr/bin/python /root/Keye/keye.py`

Now, we're done with installing and configuring Keye.

## Usage
> $ python keye.py -h

Short Form    | Long Form     | Description
------------- | ------------- |-------------
-s            | --singleurl       | Single URL to add. E.g: http://google.com
-ul           | --urlslist      | File with new URLs to add. E.g: urls.txt
-rm           | --remove       | URL to remove from database. E.g: http://google.com

## Feedback and issues?
If you have any feedback, anything that you want to see implemented or if you're running into issues using Keye, please feel free to file an issue on [https://github.com/clirimemini/Keye/issues](https://github.com/clirimemini/Keye/issues)

# FCS Fans Uploader — Privacy Policy

_Last updated: August 25, 2026_

FCS Fans Uploader ("the Tool") is a private, single-user program written and operated by the owner of the FCS Fans YouTube channel ("I", "me"). It exists for one purpose: to publish my own finished videos from my own Google Drive folder to my own YouTube channel. It has no other users, no website login, and no public interface.

## What the Tool accesses

The Tool uses Google APIs, including YouTube API Services, after I sign in with my own Google Account and grant it permission. It accesses:

- **Google Drive:** the contents of one folder that I designate. It reads video files from that folder and moves each one into an "Uploaded" subfolder after a successful upload.
- **YouTube:** my own channel, to upload videos (`videos.insert`), set their thumbnails (`thumbnails.set`), and add them to a playlist (`playlistItems.insert`).

It does not access any other person's Google Account, Drive, or YouTube data, and it does not collect information about viewers of the channel.

## How the data is used and stored

- Video files are downloaded to a server I control only for the time it takes to upload them to YouTube, then deleted from that server.
- The Google sign-in token is stored on that server so the Tool can run unattended. It is not shared with anyone.
- The Tool keeps a small log of the videos it has uploaded (file name, video title, YouTube link, date) so it does not upload the same file twice.
- No data is sold, shared with third parties, used for advertising, or used to build profiles. No analytics or tracking of any kind is performed.

## YouTube API Services

The Tool uses YouTube API Services. By using it I agree to be bound by the [YouTube Terms of Service](https://www.youtube.com/t/terms). Google's handling of data is described in the [Google Privacy Policy](https://policies.google.com/privacy).

The Tool's use of information received from Google APIs adheres to the [Google API Services User Data Policy](https://developers.google.com/terms/api-services-user-data-policy), including the Limited Use requirements.

## Revoking access

Access granted to the Tool can be revoked at any time from the Google Account permissions page at <https://myaccount.google.com/permissions>. Revoking access stops the Tool immediately; deleting the token file on the server has the same effect. Stored upload logs can be deleted at any time.

## Contact

Questions about this policy: npeskoe@gmail.com

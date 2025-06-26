 Video understanding

Gemini models can process videos, enabling many frontier developer use cases that would have historically required domain specific models. Some of Gemini's vision capabilities include the ability to:

    Describe, segment, and extract information from videos
    Answer questions about video content
    Refer to specific timestamps within a video

Gemini was built to be multimodal from the ground up and we continue to push the frontier of what is possible. This guide shows how to use the Gemini API to generate text responses based on video inputs.
Video input

You can provide videos as input to Gemini in the following ways:

    Upload a video file using the File API before making a request to generateContent. Use this method for files larger than 20MB, videos longer than approximately 1 minute, or when you want to reuse the file across multiple requests.
    Pass inline video data with the request to generateContent. Use this method for smaller files (<20MB) and shorter durations.
    Include a YouTube URL directly in the prompt.

Upload a video file

You can use the Files API to upload a video file. Always use the Files API when the total request size (including the file, text prompt, system instructions, etc.) is larger than 20 MB, the video duration is significant, or if you intend to use the same video in multiple prompts.

The File API accepts video file formats directly. This example uses the short NASA film "Jupiter's Great Red Spot Shrinks and Grows". Credit: Goddard Space Flight Center (GSFC)/David Ladd (2018).

"Jupiter's Great Red Spot Shrinks and Grows" is in the public domain and does not show identifiable people. (NASA image and media usage guidelines.)

The following code downloads the sample video, uploads it using the File API, waits for it to be processed, and then uses the file reference in a generateContent request.
Python
JavaScript
Go
REST

from google import genai

client = genai.Client(api_key="GOOGLE_API_KEY")

myfile = client.files.upload(file="path/to/sample.mp4")

response = client.models.generate_content(
    model="gemini-2.0-flash", contents=[myfile, "Summarize this video. Then create a quiz with an answer key based on the information in this video."]
)

print(response.text)

To learn more about working with media files, see Files API.
Pass video data inline

Instead of uploading a video file using the File API, you can pass smaller videos directly in the request to generateContent. This is suitable for shorter videos under 20MB total request size.

Here's an example of providing inline video data:
Python
JavaScript
REST

# Only for videos of size <20Mb
video_file_name = "/path/to/your/video.mp4"
video_bytes = open(video_file_name, 'rb').read()

response = client.models.generate_content(
    model='models/gemini-2.0-flash',
    contents=types.Content(
        parts=[
            types.Part(
                inline_data=types.Blob(data=video_bytes, mime_type='video/mp4')
            ),
            types.Part(text='Please summarize the video in 3 sentences.')
        ]
    )
)

Include a YouTube URL
Preview: The YouTube URL feature is in preview and is available at no charge. Pricing and rate limits are likely to change.

The Gemini API and AI Studio support YouTube URLs as a file data Part. You can include a YouTube URL with a prompt asking the model to summarize, translate, or otherwise interact with the video content.

Limitations:

    For the free tier, you can't upload more than 8 hours of YouTube video per day.
    For the paid tier, there is no limit based on video length.
    For models before 2.5, you can upload only 1 video per request. For models after 2.5, you can upload a maximum of 10 videos per request.
    You can only upload public videos (not private or unlisted videos).

The following example shows how to include a YouTube URL with a prompt:
Python
JavaScript
Go
REST

response = client.models.generate_content(
    model='models/gemini-2.0-flash',
    contents=types.Content(
        parts=[
            types.Part(
                file_data=types.FileData(file_uri='https://www.youtube.com/watch?v=9hE5-98ZeCg')
            ),
            types.Part(text='Please summarize the video in 3 sentences.')
        ]
    )
)

Refer to timestamps in the content

You can ask questions about specific points in time within the video using timestamps of the form MM:SS.
Python
JavaScript
Go
REST

prompt = "What are the examples given at 00:05 and 00:10 supposed to show us?" # Adjusted timestamps for the NASA video

Transcribe video and provide visual descriptions

The Gemini models can transcribe and provide visual descriptions of video content by processing both the audio track and visual frames. For visual descriptions, the model samples the video at a rate of 1 frame per second. This sampling rate may affect the level of detail in the descriptions, particularly for videos with rapidly changing visuals.
Python
JavaScript
Go
REST

prompt = "Transcribe the audio from this video, giving timestamps for salient events in the video. Also provide visual descriptions."

Customize video processing

You can customize video processing in the Gemini API by setting clipping intervals or providing custom frame rate sampling.
Tip: Video clipping and frames per second (FPS) are supported by all models, but the quality is significantly higher from 2.5 series models.
Set clipping intervals

You can clip video by specifying videoMetadata with start and end offsets.
Python

response = client.models.generate_content(
    model='models/gemini-2.5-flash-preview-05-20',
    contents=types.Content(
        parts=[
            types.Part(
                file_data=types.FileData(file_uri='https://www.youtube.com/watch?v=XEzRZ35urlk'),
                video_metadata=types.VideoMetadata(
                    start_offset='1250s',
                    end_offset='1570s'
                )
            ),
            types.Part(text='Please summarize the video in 3 sentences.')
        ]
    )
)

Set a custom frame rate

You can set custom frame rate sampling by passing an fps argument to videoMetadata.
Python

# Only for videos of size <20Mb
video_file_name = "/path/to/your/video.mp4"
video_bytes = open(video_file_name, 'rb').read()

response = client.models.generate_content(
    model='models/gemini-2.5-flash-preview-05-20',
    contents=types.Content(
        parts=[
            types.Part(
                inline_data=types.Blob(
                    data=video_bytes,
                    mime_type='video/mp4'),
                video_metadata=types.VideoMetadata(fps=5)
            ),
            types.Part(text='Please summarize the video in 3 sentences.')
        ]
    )
)

By default 1 frame per second (FPS) is sampled from the video. You might want to set low FPS (< 1) for long videos. This is especially useful for mostly static videos (e.g. lectures). If you want to capture more details in rapidly changing visuals, consider setting a higher FPS value.
Supported video formats

Gemini supports the following video format MIME types:

    video/mp4
    video/mpeg
    video/mov
    video/avi
    video/x-flv
    video/mpg
    video/webm
    video/wmv
    video/3gpp

Technical details about videos

    Supported models & context: All Gemini 2.0 and 2.5 models can process video data.
        Models with a 2M context window can process videos up to 2 hours long at default media resolution or 6 hours long at low media resolution, while models with a 1M context window can process videos up to 1 hour long at default media resolution or 3 hours long at low media resolution.
    File API processing: When using the File API, videos are sampled at 1 frame per second (FPS) and audio is processed at 1Kbps (single channel). Timestamps are added every second.
        These rates are subject to change in the future for improvements in inference.
    Token calculation: Each second of video is tokenized as follows:
        Individual frames (sampled at 1 FPS):
            If mediaResolution is set to low, frames are tokenized at 66 tokens per frame.
            Otherwise, frames are tokenized at 258 tokens per frame.
        Audio: 32 tokens per second.
        Metadata is also included.
        Total: Approximately 300 tokens per second of video at default media resolution, or 100 tokens per second of video at low media resolution.
    Timestamp format: When referring to specific moments in a video within your prompt, use the MM:SS format (e.g., 01:15 for 1 minute and 15 seconds).
    Best practices:
        Use only one video per prompt request for optimal results.
        If combining text and a single video, place the text prompt after the video part in the contents array.
        Be aware that fast action sequences might lose detail due to the 1 FPS sampling rate. Consider slowing down such clips if necessary.

What's next

This guide shows how to upload video files and generate text outputs from video inputs. To learn more, see the following resources:

    System instructions: System instructions let you steer the behavior of the model based on your specific needs and use cases.
    Files API: Learn more about uploading and managing files for use with Gemini.
    File prompting strategies: The Gemini API supports prompting with text, image, audio, and video data, also known as multimodal prompting.
    Safety guidance: Sometimes generative AI models produce unexpected outputs, such as outputs that are inaccurate, biased, or offensive. Post-processing and human evaluation are essential to limit the risk of harm from such outputs.



 Structured output

You can configure Gemini for structured output instead of unstructured text, allowing precise extraction and standardization of information for further processing. For example, you can use structured output to extract information from resumes, standardize them to build a structured database.

Gemini can generate either JSON or enum values as structured output.
Generating JSON

There are two ways to generate JSON using the Gemini API:

    Configure a schema on the model
    Provide a schema in a text prompt

Configuring a schema on the model is the recommended way to generate JSON, because it constrains the model to output JSON.
Configuring a schema (recommended)

To constrain the model to generate JSON, configure a responseSchema. The model will then respond to any prompt with JSON-formatted output.
Python
JavaScript
Go
REST

from google import genai
from pydantic import BaseModel

class Recipe(BaseModel):
    recipe_name: str
    ingredients: list[str]

client = genai.Client(api_key="GOOGLE_API_KEY")
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="List a few popular cookie recipes, and include the amounts of ingredients.",
    config={
        "response_mime_type": "application/json",
        "response_schema": list[Recipe],
    },
)
# Use the response as a JSON string.
print(response.text)

# Use instantiated objects.
my_recipes: list[Recipe] = response.parsed

Note: Pydantic validators are not yet supported. If a pydantic.ValidationError occurs, it is suppressed, and .parsed may be empty/null.

The output might look like this:

[
  {
    "recipeName": "Chocolate Chip Cookies",
    "ingredients": [
      "1 cup (2 sticks) unsalted butter, softened",
      "3/4 cup granulated sugar",
      "3/4 cup packed brown sugar",
      "1 teaspoon vanilla extract",
      "2 large eggs",
      "2 1/4 cups all-purpose flour",
      "1 teaspoon baking soda",
      "1 teaspoon salt",
      "2 cups chocolate chips"
    ]
  },
  ...
]

Providing a schema in a text prompt

Instead of configuring a schema, you can supply a schema as natural language or pseudo-code in a text prompt. This method is not recommended, because it might produce lower quality output, and because the model is not constrained to follow the schema.
Warning: Don't provide a schema in a text prompt if you're configuring a responseSchema. This can produce unexpected or low quality results.

Here's a generic example of a schema provided in a text prompt:

List a few popular cookie recipes, and include the amounts of ingredients.

Produce JSON matching this specification:

Recipe = { "recipeName": string, "ingredients": array<string> }
Return: array<Recipe>

Since the model gets the schema from text in the prompt, you might have some flexibility in how you represent the schema. But when you supply a schema inline like this, the model is not actually constrained to return JSON. For a more deterministic, higher quality response, configure a schema on the model, and don't duplicate the schema in the text prompt.
Generating enum values

In some cases you might want the model to choose a single option from a list of options. To implement this behavior, you can pass an enum in your schema. You can use an enum option anywhere you could use a string in the responseSchema, because an enum is an array of strings. Like a JSON schema, an enum lets you constrain model output to meet the requirements of your application.

For example, assume that you're developing an application to classify musical instruments into one of five categories: "Percussion", "String", "Woodwind", "Brass", or ""Keyboard"". You could create an enum to help with this task.

In the following example, you pass an enum as the responseSchema, constraining the model to choose the most appropriate option.
Python
JavaScript
REST

from google import genai
import enum

class Instrument(enum.Enum):
  PERCUSSION = "Percussion"
  STRING = "String"
  WOODWIND = "Woodwind"
  BRASS = "Brass"
  KEYBOARD = "Keyboard"

client = genai.Client(api_key="GEMINI_API_KEY")
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What type of instrument is an oboe?',
    config={
        'response_mime_type': 'text/x.enum',
        'response_schema': Instrument,
    },
)

print(response.text)
# Woodwind

The Python library will translate the type declarations for the API. However, the API accepts a subset of the OpenAPI 3.0 schema (Schema).

There are two other ways to specify an enumeration. You can use a Literal: ```
Python

Literal["Percussion", "String", "Woodwind", "Brass", "Keyboard"]

And you can also pass the schema as JSON:
Python

from google import genai

client = genai.Client(api_key="GEMINI_API_KEY")
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What type of instrument is an oboe?',
    config={
        'response_mime_type': 'text/x.enum',
        'response_schema': {
            "type": "STRING",
            "enum": ["Percussion", "String", "Woodwind", "Brass", "Keyboard"],
        },
    },
)

print(response.text)
# Woodwind

Beyond basic multiple choice problems, you can use an enum anywhere in a JSON schema. For example, you could ask the model for a list of recipe titles and use a Grade enum to give each title a popularity grade:
Python

from google import genai

import enum
from pydantic import BaseModel

class Grade(enum.Enum):
    A_PLUS = "a+"
    A = "a"
    B = "b"
    C = "c"
    D = "d"
    F = "f"

class Recipe(BaseModel):
  recipe_name: str
  rating: Grade

client = genai.Client(api_key="GEMINI_API_KEY")
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='List 10 home-baked cookie recipes and give them grades based on tastiness.',
    config={
        'response_mime_type': 'application/json',
        'response_schema': list[Recipe],
    },
)

print(response.text)

The response might look like this:

[
  {
    "recipe_name": "Chocolate Chip Cookies",
    "rating": "a+"
  },
  {
    "recipe_name": "Peanut Butter Cookies",
    "rating": "a"
  },
  {
    "recipe_name": "Oatmeal Raisin Cookies",
    "rating": "b"
  },
  ...
]

About JSON schemas

Configuring the model for JSON output using responseSchema parameter relies on Schema object to define its structure. This object represents a select subset of the OpenAPI 3.0 Schema object, and also adds a propertyOrdering field.
Tip: On Python, when you use a Pydantic model, you don't need to directly work with Schema objects, as it gets automatically converted to the corresponding JSON schema. To learn more, see JSON schemas in Python.

Here's a pseudo-JSON representation of all the Schema fields:

{
  "type": enum (Type),
  "format": string,
  "description": string,
  "nullable": boolean,
  "enum": [
    string
  ],
  "maxItems": integer,
  "minItems": integer,
  "properties": {
    string: {
      object (Schema)
    },
    ...
  },
  "required": [
    string
  ],
  "propertyOrdering": [
    string
  ],
  "items": {
    object (Schema)
  }
}

The Type of the schema must be one of the OpenAPI Data Types, or a union of those types (using anyOf). Only a subset of fields is valid for each Type. The following list maps each Type to a subset of the fields that are valid for that type:

    string -> enum, format, nullable
    integer -> format, minimum, maximum, enum, nullable
    number -> format, minimum, maximum, enum, nullable
    boolean -> nullable
    array -> minItems, maxItems, items, nullable
    object -> properties, required, propertyOrdering, nullable

Here are some example schemas showing valid type-and-field combinations:

{ "type": "string", "enum": ["a", "b", "c"] }

{ "type": "string", "format": "date-time" }

{ "type": "integer", "format": "int64" }

{ "type": "number", "format": "double" }

{ "type": "boolean" }

{ "type": "array", "minItems": 3, "maxItems": 3, "items": { "type": ... } }

{ "type": "object",
  "properties": {
    "a": { "type": ... },
    "b": { "type": ... },
    "c": { "type": ... }
  },
  "nullable": true,
  "required": ["c"],
  "propertyOrdering": ["c", "b", "a"]
}

For complete documentation of the Schema fields as they're used in the Gemini API, see the Schema reference.
Property ordering
Warning: When you're configuring a JSON schema, make sure to set propertyOrdering[], and when you provide examples, make sure that the property ordering in the examples matches the schema.

When you're working with JSON schemas in the Gemini API, the order of properties is important. By default, the API orders properties alphabetically and does not preserve the order in which the properties are defined (although the Google Gen AI SDKs may preserve this order). If you're providing examples to the model with a schema configured, and the property ordering of the examples is not consistent with the property ordering of the schema, the output could be rambling or unexpected.

To ensure a consistent, predictable ordering of properties, you can use the optional propertyOrdering[] field.

"propertyOrdering": ["recipeName", "ingredients"]

propertyOrdering[] – not a standard field in the OpenAPI specification – is an array of strings used to determine the order of properties in the response. By specifying the order of properties and then providing examples with properties in that same order, you can potentially improve the quality of results. propertyOrdering is only supported when you manually create types.Schema.
Schemas in Python

When you're using the Python library, the value of response_schema must be one of the following:

    A type, as you would use in a type annotation (see the Python typing module)
    An instance of genai.types.Schema
    The dict equivalent of genai.types.Schema

The easiest way to define a schema is with a Pydantic type (as shown in the previous example):
Python

config={'response_mime_type': 'application/json',
        'response_schema': list[Recipe]}

When you use a Pydantic type, the Python library builds out a JSON schema for you and sends it to the API. For additional examples, see the Python library docs.

The Python library supports schemas defined with the following types (where AllowedType is any allowed type):

    int
    float
    bool
    str
    list[AllowedType]
    AllowedType|AllowedType|...
    For structured types:
        dict[str, AllowedType]. This annotation declares all dict values to be the same type, but doesn't specify what keys should be included.
        User-defined Pydantic models. This approach lets you specify the key names and define different types for the values associated with each of the keys, including nested structures.

JSON Schema support

JSON Schema is a more recent specification than OpenAPI 3.0, which the Schema object is based on. Support for JSON Schema is available as a preview using the field responseJsonSchema which accepts any JSON Schema with the following limitations:

    It only works with Gemini 2.5.
    While all JSON Schema properties can be passed, not all are supported. See the documentation for the field for more details.
    Recursive references can only be used as the value of a non-required object property.
    Recursive references are unrolled to a finite degree, based on the size of the schema.
    Schemas that contain $ref cannot contain any properties other than those starting with a $.

Here's an example of generating a JSON Schema with Pydantic and submitting it to the model:

curl "https://generativelanguage.googleapis.com/v1alpha/models/\
gemini-2.5-flash:generateContent?key=$GEMINI_API_KEY" \
    -H 'Content-Type: application/json' \
    -d @- <<EOF
{
  "contents": [{
    "parts":[{
      "text": "Please give a random example following this schema"
    }]
  }],
  "generationConfig": {
    "response_mime_type": "application/json",
    "response_json_schema": $(python3 - << PYEOF
from enum import Enum
from typing import List, Optional, Union, Set
from pydantic import BaseModel, Field, ConfigDict
import json

class UserRole(str, Enum):
    ADMIN = "admin"
    VIEWER = "viewer"

class Address(BaseModel):
    street: str
    city: str

class UserProfile(BaseModel):
    username: str = Field(description="User's unique name")
    age: Optional[int] = Field(ge=0, le=120)
    roles: Set[UserRole] = Field(min_items=1)
    contact: Union[Address, str]
    model_config = ConfigDict(title="User Schema")

# Generate and print the JSON Schema
print(json.dumps(UserProfile.model_json_schema(), indent=2))
PYEOF
)
  }
}
EOF

Passing JSON Schema directly is not yet supported when using the SDK.
Best practices

Keep the following considerations and best practices in mind when you're using a response schema:

    The size of your response schema counts towards the input token limit.
    By default, fields are optional, meaning the model can populate the fields or skip them. You can set fields as required to force the model to provide a value. If there's insufficient context in the associated input prompt, the model generates responses mainly based on the data it was trained on.

    A complex schema can result in an InvalidArgument: 400 error. Complexity might come from long property names, long array length limits, enums with many values, objects with lots of optional properties, or a combination of these factors.

    If you get this error with a valid schema, make one or more of the following changes to resolve the error:
        Shorten property names or enum names.
        Flatten nested arrays.
        Reduce the number of properties with constraints, such as numbers with minimum and maximum limits.
        Reduce the number of properties with complex constraints, such as properties with complex formats like date-time.
        Reduce the number of optional properties.
        Reduce the number of valid values for enums.

    If you aren't seeing the results you expect, add more context to your input prompts or revise your response schema. For example, review the model's response without structured output to see how the model responds. You can then update your response schema so that it better fits the model's output.


 Files API

The Gemini family of artificial intelligence (AI) models is built to handle various types of input data, including text, images, and audio. Since these models can handle more than one type or mode of data, the Gemini models are called multimodal models or explained as having multimodal capabilities.

This guide shows you how to work with media files using the Files API. The basic operations are the same for audio files, images, videos, documents, and other supported file types.

For file prompting guidance, check out the File prompt guide section.
Upload a file

You can use the Files API to upload a media file. Always use the Files API when the total request size (including the files, text prompt, system instructions, etc.) is larger than 20 MB.

The following code uploads a file and then uses the file in a call to generateContent.
Python
JavaScript
Go
REST

from google import genai

client = genai.Client(api_key="GOOGLE_API_KEY")

myfile = client.files.upload(file="path/to/sample.mp3")

response = client.models.generate_content(
    model="gemini-2.0-flash", contents=["Describe this audio clip", myfile]
)

print(response.text)

Get metadata for a file

You can verify that the API successfully stored the uploaded file and get its metadata by calling files.get.
Python
JavaScript
Go
REST

myfile = client.files.upload(file='path/to/sample.mp3')
file_name = myfile.name
myfile = client.files.get(name=file_name)
print(myfile)

List uploaded files

You can upload multiple files using the Files API. The following code gets a list of all the files uploaded:
Python
JavaScript
Go
REST

print('My files:')
for f in client.files.list():
    print(' ', f.name)

Delete uploaded files

Files are automatically deleted after 48 hours. You can also manually delete an uploaded file:
Python
JavaScript
Go
REST

myfile = client.files.upload(file='path/to/sample.mp3')
client.files.delete(name=myfile.name)

Usage info
You can use the Files API to upload and interact with media files. The Files API lets you store up to 20 GB of files per project, with a per-file maximum size of 2 GB. Files are stored for 48 hours. During that time, you can use the API to get metadata about the files, but you can't download the files. The Files API is available at no cost in all regions where the Gemini API is available.

# Use an official Python runtime as an image
FROM python:3.9 

# EXPOSE instruction indicates the ports on which a container
# will listen for connections
# Flask apps listen to port 5000 by default, so we expose it 
EXPOSE 5000

# WORDIR sets the working directory for following COPY and CMD 
# instructions 
# Notice we haven't created a directory by this name - this 
# instruction creates a directory with this name if it doesn't exist 
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app
RUN pip install -r requirements.txt 

# Run app.py when the container launches 
ADD templates /app/templates
COPY models.py /app
COPY app.py /app
COPY social_media_dash.db /app
COPY dashboard_config.cfg /app
CMD python app.py
